from django.conf import settings as django_settings
from rest_framework.reverse import reverse

from nodeconductor.core.utils import request_api
from nodeconductor.structure import ServiceBackend, ServiceBackendError
from nodeconductor_jira.models import Project, Issue


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
        pass

    def provision(self, deployment, request, ssh_key=None):
        try:
            proj = Project.objects.get(backend_id=self.settings.token, available_for_all=True)
        except Project.DoesNotExist:
            self._set_erred(deployment, "Can't find JIRA project '%s'" % self.settings.token)

        # create fake and empty SshKey instance for string formating
        if not ssh_key:
            ssh_key = type('SshKey', (object,), {'name': '', 'uuid': type('UUID', (object,), {'hex': ''})})

        message = self._compile_message(deployment, 'provision', ssh_key=ssh_key)
        payload = {
            "project": reverse('jira-projects-detail', kwargs={'uuid': proj.uuid.hex}),
            "summary": self.templates['provision']['summary'],
            "description": message,
            "priority": dict(Issue.Priority.CHOICES).get(Issue.Priority.MINOR),
            "impact": dict(Issue.Impact.CHOICES).get(Issue.Impact.MEDIUM),
        }

        response = request_api(request, 'jira-issues-list', method='POST', data=payload)
        if not response.success:
            self._set_erred(deployment, "Can't create JIRA ticket: %s" % response.status)

        deployment.support_request = Issue.objects.get(uuid=response.data['uuid'])
        deployment.begin_provisioning()
        deployment.save(update_fields=['state'])

    def destroy(self, deployment, request):
        payload = {
            "issue": reverse('jira-issues-detail', kwargs={'uuid': deployment.support_request.uuid.hex}),
            "message": self._compile_message(deployment, 'undeploy'),
        }
        response = request_api(request, 'jira-comments-list', method='POST', data=payload)
        if not response.success:
            self._set_erred(deployment, "Can't add JIRA comment: %s" % response.status)

        deployment.begin_deleting()
        deployment.save(update_fields=['state'])

    def resize(self, deployment, request):
        payload = {
            "issue": reverse('jira-issues-detail', kwargs={'uuid': deployment.support_request.uuid.hex}),
            "message": self._compile_message(deployment, 'resize'),
        }
        response = request_api(request, 'jira-comments-list', method='POST', data=payload)
        if not response.success:
            self._set_erred(deployment, "Can't add JIRA comment: %s" % response.status)

        deployment.begin_resizing()
        deployment.save(update_fields=['state'])

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

    def _set_erred(self, deployment, message=''):
        deployment.error_message = message
        deployment.set_erred()
        deployment.save(update_fields=['state', 'error_message'])
        raise OracleBackendError(deployment.error_message)
