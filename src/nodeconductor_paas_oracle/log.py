from nodeconductor.logging.loggers import EventLogger, event_logger
from nodeconductor_paas_oracle.models import Deployment


class OracleDeploymentEventLogger(EventLogger):
    deployment = Deployment
    jira_issue_key = basestring

    class Meta:
        nullable_fields = ['jira_issue_key']
        event_types = (
            'oracle_deployment_resize_requested',
            'oracle_deployment_resize_succeeded',
            'oracle_deployment_start_requested',
            'oracle_deployment_start_succeeded',
            'oracle_deployment_restart_requested',
            'oracle_deployment_restart_succeeded',
            'oracle_deployment_stop_requested',
            'oracle_deployment_stop_succeeded',
            'oracle_deployment_support_requested',
            'oracle_deployment_report_updated',
        )


event_logger.register('oracle_deployment', OracleDeploymentEventLogger)
