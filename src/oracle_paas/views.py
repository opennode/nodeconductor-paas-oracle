from django.utils import timezone
from rest_framework import decorators, response, status

from nodeconductor.structure import views as structure_views

from . import models, serializers


class OracleServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.OracleService.objects.all()
    serializer_class = serializers.ServiceSerializer


class OracleServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.OracleServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer


class DeployViewSet(structure_views.BaseResourceViewSet):
    queryset = models.Deploy.objects.all()
    serializer_class = serializers.DeploySerializer

    def perform_provision(self, serializer):
        resource = serializer.save()
        resource.begin_provisioning()
        resource.save()

    @decorators.detail_route(methods=['post'])
    def provision(self, request, uuid=None):
        """ Complete provisioning. Example:

            .. code-block:: http

                POST /api/oracle-deploys/a04a26e46def4724a0841abcb81926ac/provision/ HTTP/1.1
                Content-Type: application/json
                Accept: application/json
                Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
                Host: example.com

                {
                    "report": "ORACONF=TST12DB\n\nDBTYPE=single\nDBNAME='TST12DB'"
                }
        """
        report = request.data.get('report')
        if report:
            resource = self.get_object()
            resource.report = report
            resource.start_time = timezone.now()
            resource.set_online()
            resource.save()
            return response.Response({'detail': "Provision complete"}, status=status.HTTP_200_OK)
        else:
            return response.Response({'detail': "Empty report"}, status=status.HTTP_400_BAD_REQUEST)
