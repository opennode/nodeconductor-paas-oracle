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

        return self._jira_ticket('provision', deployment, request, ssh_key=ssh_key)

    def destroy(self, deployment, request):
        return self._jira_ticket('undeploy', deployment, request)

    def resize(self, deployment, request):
        return self._jira_ticket('resize', deployment, request)

    def stop(self, deployment, request, message="Request for stopping Oracle DB PaaS instance"):
        return self._jira_ticket('support', deployment, request, message=message)

    def start(self, deployment, request, message="Request for starting Oracle DB PaaS instance"):
        return self._jira_ticket('support', deployment, request, message=message)

    def restart(self, deployment, request, message="Request for restarting Oracle DB PaaS instance"):
        return self._jira_ticket('support', deployment, request, message=message)

    def support_request(self, deployment, request, message):
        return self._jira_ticket('support', deployment, request, message=message)

    def _jira_ticket(self, name, deployment, request, **kwargs):
        self.sync()  # fetch project

        template = self.templates[name]
        message = unicode(template['details']).format(
            deployment=deployment,
            customer=deployment.service_project_link.service.customer,
            project=deployment.service_project_link.project,
            **kwargs)

        payload = {
            "project": reverse('jira-projects-detail', kwargs={'uuid': self.project.uuid.hex}),
            "summary": template['summary'],
            "description": message,
            "priority": dict(Issue.Priority.CHOICES).get(Issue.Priority.MINOR),
            "impact": dict(Issue.Impact.CHOICES).get(Issue.Impact.MEDIUM),
        }

        response = request_api(request, 'jira-issues-list', method='POST', data=payload)
        if not response.ok:
            logger.error('[%s] Failed request to %s: %s' % (
                response.status_code, response.url, response.text))
            raise OracleBackendError("Can't create JIRA ticket: %s" % response.text)

        data = response.json()
        issue = Issue.objects.get(uuid=data['uuid'])
        deployment.support_requests.add(issue)
        return issue
