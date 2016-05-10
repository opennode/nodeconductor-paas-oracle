from functools import wraps
from django.utils import timezone
from rest_framework import decorators, exceptions, response, status

from nodeconductor.structure import views as structure_views

from . import models, serializers
from .backend import OracleBackendError


States = models.Deployment.States


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


class FlavorViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Flavor.objects.order_by('cores', 'ram', 'disk')
    serializer_class = serializers.FlavorSerializer
    lookup_field = 'uuid'


class DeploymentViewSet(structure_views.BaseResourceViewSet):
    queryset = models.Deployment.objects.all()
    serializer_class = serializers.DeploymentSerializer

    def get_serializer_class(self):
        if self.action == 'resize':
            return serializers.DeploymentResizeSerializer
        elif self.action == 'support':
            return serializers.SupportSerializer
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
    @structure_views.safe_operation(valid_state=States.PROVISIONING)
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
            resource.report = report
            resource.start_time = timezone.now()
            resource.set_online()
            resource.save(update_fields=['report', 'start_time', 'state'])
            return response.Response({'detail': "Provision complete"})
        else:
            return response.Response({'detail': "Empty report"}, status=status.HTTP_400_BAD_REQUEST)

    @decorators.detail_route(methods=['post'])
    @structure_views.safe_operation()
    def update_report(self, request, resource, uuid=None):
        """ Update provisioning report. Example:

            .. code-block:: http

                POST /api/oracle-deployments/a04a26e46def4724a0841abcb81926ac/update_report/ HTTP/1.1
                Content-Type: application/json
                Accept: application/json
                Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
                Host: example.com

                {
                    "report": "ORACONF=TST12DB\n\nDBTYPE=single\nDBNAME='PRD12DB'"
                }
        """
        if not self.request.user.is_staff:
            raise exceptions.PermissionDenied

        report = request.data.get('report')
        if report:
            resource.report = report
            resource.save(update_fields=['report'])
            return response.Response({'detail': "Report has been updated"})
        else:
            return response.Response({'detail': "Empty report"}, status=status.HTTP_400_BAD_REQUEST)

    @structure_views.safe_operation(valid_state=States.ONLINE)
    @track_exceptions
    def support(self, request, resource, uuid=None):
        """ File custom support request.

            .. code-block:: http

                POST /api/oracle-deployments/a04a26e46def4724a0841abcb81926ac/support/ HTTP/1.1
                Content-Type: application/json
                Accept: application/json
                Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
                Host: example.com

                {
                    "message": "Could you make that DB running faster?\n\nThanks."
                }
        """

        serializer = self.get_serializer(resource, data=request.data)
        serializer.is_valid(raise_exception=True)
        backend = resource.get_backend()
        backend.support_request(resource, self.request, serializer.validated_data['message'])
        return response.Response({'detail': "Support request accepted"})

    @decorators.detail_route(methods=['post'])
    @structure_views.safe_operation(valid_state=(States.ONLINE, States.RESIZING))
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

        if resource.state == States.RESIZING:
            if not self.request.user.is_staff:
                raise exceptions.PermissionDenied
            resource.set_resized()
            resource.save(update_fields=['state'])
            return response.Response({'detail': "Resizing complete"})

        serializer = self.get_serializer(resource, data=request.data)
        serializer.is_valid(raise_exception=True)

        resource.state = States.RESIZING_SCHEDULED
        resource.flavor = serializer.validated_data.get('flavor')
        resource.save(update_fields=['flavor', 'state'])

        backend = resource.get_backend()
        backend.resize(resource, self.request)

        resource.begin_resizing()
        resource.save(update_fields=['state'])
        return response.Response({'detail': "Resizing scheduled"})

    @structure_views.safe_operation(valid_state=(States.OFFLINE, States.DELETING))
    @track_exceptions
    def destroy(self, request, resource, uuid=None):
        """ Request for DB Instance deletion or confirm deletion success.
            A proper action will be taken depending on the current deployment state.
        """

        if resource.state == States.DELETING:
            if not self.request.user.is_staff:
                raise exceptions.PermissionDenied
            self.perform_destroy(resource)
            return response.Response({'detail': "Deployment deleted"})

        resource.schedule_deletion()
        resource.save(update_fields=['state'])

        backend = resource.get_backend()
        backend.destroy(resource, self.request)

        resource.begin_deleting()
        resource.save(update_fields=['state'])
        return response.Response({'detail': "Deletion scheduled"})

    @decorators.detail_route(methods=['post'])
    @structure_views.safe_operation(valid_state=(States.OFFLINE, States.STARTING))
    def start(self, request, resource, uuid=None):
        """ Request for DB Instance starting or confirm starting success.
            A proper action will be taken depending on the current deployment state.
        """

        if resource.state == States.STARTING:
            if not self.request.user.is_staff:
                raise exceptions.PermissionDenied
            else:
                resource.set_online()
                resource.save(update_fields=['state'])
                return response.Response({'detail': "Deployment started"})

        resource.schedule_starting()
        resource.save(update_fields=['state'])

        backend = resource.get_backend()
        backend.start(resource, self.request)

        resource.begin_starting()
        resource.save(update_fields=['state'])
        return response.Response({'detail': "Starting scheduled"})

    @decorators.detail_route(methods=['post'])
    @structure_views.safe_operation(valid_state=(States.ONLINE, States.STOPPING))
    def stop(self, request, resource, uuid=None):
        """ Request for DB Instance stopping or confirm stopping success.
            A proper action will be taken depending on the current deployment state.
        """

        if resource.state == States.STOPPING:
            if not self.request.user.is_staff:
                raise exceptions.PermissionDenied
            else:
                resource.set_offline()
                resource.save(update_fields=['state'])
                return response.Response({'detail': "Deployment stopped"})

        resource.schedule_stopping()
        resource.save(update_fields=['state'])

        backend = resource.get_backend()
        backend.stop(resource, self.request)

        resource.begin_stopping()
        resource.save(update_fields=['state'])
        return response.Response({'detail': "Stopping scheduled"})

    @decorators.detail_route(methods=['post'])
    @structure_views.safe_operation(valid_state=(States.ONLINE, States.RESTARTING))
    def restart(self, request, resource, uuid=None):
        """ Request for DB Instance restarting or confirm restarting success.
            A proper action will be taken depending on the current deployment state.
        """

        if resource.state == States.RESTARTING:
            if not self.request.user.is_staff:
                raise exceptions.PermissionDenied
            else:
                resource.set_online()
                resource.save(update_fields=['state'])
                return response.Response({'detail': "Deployment restarted"})

        resource.schedule_restarting()
        resource.save(update_fields=['state'])

        backend = resource.get_backend()
        backend.restart(resource, self.request)

        resource.begin_restarting()
        resource.save(update_fields=['state'])
        return response.Response({'detail': "Restarting scheduled"})
