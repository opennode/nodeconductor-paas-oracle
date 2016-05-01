import logging

from django.conf import settings as django_settings
from rest_framework.reverse import reverse

from nodeconductor.core.utils import request_api
from nodeconductor.structure import ServiceBackend, ServiceBackendError
from nodeconductor_jira.models import Project, Issue

logger = logging.getLogger(__name__)


class OracleBackendError(ServiceBackendError):
    pass


class OracleBackend(ServiceBackend):

    def __init__(self, settings):
        self.settings = settings
        self.templates = getattr(django_settings, 'ORACLE_TICKET_TEMPLATES', {})

        if not self.templates or 'provision' not in self.templates:
            raise OracleBackendError(
                "Improperly configured: ORACLE_TICKET_TEMPLATES should be defined")

    def ping(self, raise_exception=False):
        return True

    def sync(self):
        try:
            self.project = Project.objects.get(
                backend_id=self.settings.token, available_for_all=True)
        except Project.DoesNotExist:
            raise OracleBackendError("Can't find JIRA project '%s'" % self.settings.token)

    def provision(self, deployment, request, ssh_key=None):
        # create fake and empty SshKey instance for string formatting
        if not ssh_key:
            ssh_key = type('SshKey', (object,), {'name': '', 'uuid': type('UUID', (object,), {'hex': ''})})

        self.sync()  # fetch project
        message = self._compile_message(deployment, 'provision', ssh_key=ssh_key)
        payload = {
            "project": reverse('jira-projects-detail', kwargs={'uuid': self.project.uuid.hex}),
            "summary": self.templates['provision']['summary'],
            "description": message,
            "priority": dict(Issue.Priority.CHOICES).get(Issue.Priority.MINOR),
            "impact": dict(Issue.Impact.CHOICES).get(Issue.Impact.MEDIUM),
        }

        data = self._jira_request(
            'jira-issues-list', request, data=payload, error_message="Can't create JIRA ticket")
        deployment.support_request = Issue.objects.get(uuid=data['uuid'])
        deployment.save(update_fields=['support_request'])

    def destroy(self, deployment, request):
        self._support_request('undeploy', deployment, request)

    def resize(self, deployment, request):
        self._support_request('resize', deployment, request)

    def support_request(self, deployment, request, message):
        self._support_request('support', deployment, request, message=message)

    def _support_request(self, name, deployment, request, **kwargs):
        issue = reverse('jira-issues-detail', kwargs={'uuid': deployment.support_request.uuid.hex})
        self._jira_request(
            'jira-comments-list',
            request,
            data={
                "issue": issue,
                "message": self._compile_message(deployment, name, add_title=True, **kwargs),
            },
            error_message="Can't add JIRA comment")

    def _jira_request(self, view_name, request, data=None, error_message="Request failed"):
        response = request_api(request, view_name, method='POST' if data else 'GET', data=data)
        if not response.ok:
            logger.error('[%s] Failed request to %s: %s' % (
                response.status_code, response.url, response.text))
            error_message += ': %s'
            raise OracleBackendError(error_message % response.text)
        return response.json()

    def _compile_message(self, deployment, template_name, add_title=False, **kwargs):
        template = self.templates[template_name]
        message = unicode(template['details']).format(
            deployment=deployment,
            customer=deployment.service_project_link.service.customer,
            project=deployment.service_project_link.project,
            **kwargs)

        if add_title:
            message = template['summary'] + '\n\n' + message

        return message
