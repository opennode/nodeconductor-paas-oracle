from django.apps import AppConfig


class OracleConfig(AppConfig):
    name = 'nodeconductor_paas_oracle'
    verbose_name = 'Oracle'
    service_name = 'Oracle'

    def ready(self):
        from nodeconductor.structure import SupportedServices

        # structure
        from .backend import OracleBackend
        SupportedServices.register_backend(OracleBackend)
