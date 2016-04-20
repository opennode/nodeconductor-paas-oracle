from nodeconductor.core import NodeConductorExtension


class OracleExtension(NodeConductorExtension):

    @staticmethod
    def django_app():
        return 'oracle_paas'

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in
