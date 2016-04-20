from django.apps import AppConfig


class OracleConfig(AppConfig):
    name = 'oracle_paas'
    verbose_name = 'Oracle'
    service_name = 'Oracle'

    def ready(self):
        from nodeconductor.structure import SupportedServices
        from .backend import OracleBackend
        SupportedServices.register_backend(OracleBackend)
