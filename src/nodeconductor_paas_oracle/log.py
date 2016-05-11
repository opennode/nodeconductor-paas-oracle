from nodeconductor.logging.loggers import EventLogger, event_logger
from nodeconductor_saltstack.saltstack.models import SaltStackProperty


class OracleDeploymentEventLogger(EventLogger):
    property = SaltStackProperty

    class Meta:
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
