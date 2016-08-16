from django.apps import AppConfig


class OracleConfig(AppConfig):
    name = 'nodeconductor_paas_oracle'
    verbose_name = 'Oracle'
    service_name = 'Oracle'

    def ready(self):
        from nodeconductor.structure import SupportedServices
        from nodeconductor.cost_tracking import CostTrackingRegister

        # structure
        from .backend import OracleBackend
        SupportedServices.register_backend(OracleBackend)

        # cost tracking
        from .cost_tracking import OracleCostTrackingBackend
        CostTrackingRegister.register(self.label, OracleCostTrackingBackend)
