from nodeconductor.structure import ServiceBackend


class OracleBackend(ServiceBackend):

    def __init__(self, settings):
        self.settings = settings

    def ping(self, raise_exception=False):
        return True

    def sync(self):
        pass
