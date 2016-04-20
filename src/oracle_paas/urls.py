from . import views


def register_in(router):
    router.register(r'oracle', views.OracleServiceViewSet, base_name='oracle')
    router.register(r'oracle-service-project-link', views.OracleServiceProjectLinkViewSet, base_name='oracle-spl')
    router.register(r'oracle-deploys', views.DeployViewSet, base_name='oracle-deploys')
