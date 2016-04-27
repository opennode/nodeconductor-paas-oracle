from functools import wraps
from django.utils import timezone
from rest_framework import decorators, exceptions, response, status

from nodeconductor.structure import views as structure_views

from . import models, serializers
from .backend import OracleBackendError


def track_exceptions(view_fn):
    @wraps(view_fn)
    def wrapped(self, request, resource, *args, **kwargs):
        try:
            return view_fn(self, request, resource, *args, **kwargs)
        except OracleBackendError as e:
            resource.error_message = unicode(e)
            resource.set_erred()
            resource.save(update_fields=['state', 'error_message'])
            raise exceptions.APIException(e)
    return wrapped


class OracleServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.OracleService.objects.all()
    serializer_class = serializers.ServiceSerializer


class OracleServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.OracleServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer


class DeploymentViewSet(structure_views.BaseResourceViewSet):
    queryset = models.Deployment.objects.all()
    serializer_class = serializers.DeploymentSerializer

    def get_serializer_class(self):
        if self.action == 'resize':
            return serializers.DeploymentResizeSerializer
        return super(DeploymentViewSet, self).get_serializer_class()

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()

        try:
            backend.provision(
                resource, self.request, ssh_key=serializer.validated_data.get('ssh_public_key'))
        except OracleBackendError as e:
            resource.error_message = unicode(e)
            resource.set_erred()
            resource.save(update_fields=['state', 'error_message'])
            raise

        resource.begin_provisioning()
        resource.save(update_fields=['state'])

    @decorators.detail_route(methods=['post'])
    @structure_views.safe_operation(valid_state=models.Deployment.States.PROVISIONING)
    def provision(self, request, resource, uuid=None):
        """ Complete provisioning. Example:

            .. code-block:: http

                POST /api/oracle-deployments/a04a26e46def4724a0841abcb81926ac/provision/ HTTP/1.1
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
            resource.save(update_fields=['state'])
            return response.Response({'detail': "Provision complete"}, status=status.HTTP_200_OK)
        else:
            return response.Response({'detail': "Empty report"}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.detail_route(methods=['post'])
    @structure_views.safe_operation(valid_state=(models.Deployment.States.ONLINE, models.Deployment.States.RESIZING))
    def resize(self, request, resource, uuid=None):
        """ Request for DB Instance resize. Example:

            .. code-block:: http

                POST /api/oracle-deployments/a04a26e46def4724a0841abcb81926ac/resize/ HTTP/1.1
                Content-Type: application/json
                Accept: application/json
                Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
                Host: example.com

                {
                    "flavor": "http://example.com/api/openstack-flavors/ef86802458684056b18576a91daf7690/"
                }

            To confirm resize complete issue an empty post to the same endpoint.
        """

        if resource.state == resource.States.RESIZING:
            if not self.request.user.is_staff:
                raise exceptions.PermissionDenied
            resource.set_resized()
            resource.save(update_fields=['state'])
            return response.Response({'detail': "Resizing complete"}, status=status.HTTP_200_OK)

        serializer = self.get_serializer(resource, data=request.data)
        serializer.is_valid(raise_exception=True)

        resource.state = resource.States.RESIZING_SCHEDULED
        resource.flavor = serializer.validated_data.get('flavor')
        resource.save(update_fields=['flavor', 'state'])

        backend = resource.get_backend()
        backend.resize(resource, self.request)

        resource.begin_resizing()
        resource.save(update_fields=['state'])
        return response.Response({'detail': "Resizing scheduled"}, status=status.HTTP_200_OK)

    @structure_views.safe_operation(valid_state=(models.Deployment.States.ONLINE, models.Deployment.States.DELETING))
    @track_exceptions
    def destroy(self, request, resource, uuid=None):
        """ Request for DB Instance deletion or confirm deletion success.
            A proper action will be taken depending on the current deployment state.
        """

        if resource.state == resource.States.DELETING:
            if not self.request.user.is_staff:
                raise exceptions.PermissionDenied
            self.perform_destroy(resource)
            return response.Response({'detail': "Deployment deleted"}, status=status.HTTP_200_OK)

        resource.state = resource.States.DELETION_SCHEDULED
        resource.save(update_fields=['state'])

        backend = resource.get_backend()
        backend.destroy(resource, self.request)

        resource.begin_deleting()
        resource.save(update_fields=['state'])
        return response.Response({'detail': "Deletion scheduled"}, status=status.HTTP_200_OK)
