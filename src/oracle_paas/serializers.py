from rest_framework import serializers

from nodeconductor.structure import serializers as structure_serializers

from . import models


class ServiceSerializer(structure_serializers.BaseServiceSerializer):

    SERVICE_ACCOUNT_FIELDS = {
        'backend_url': 'Responsible JIRA project URL (e.g. https://jira.example.com/projects/TST/)',
    }

    class Meta(structure_serializers.BaseServiceSerializer.Meta):
        model = models.OracleService
        view_name = 'oracle-detail'


class ServiceProjectLinkSerializer(structure_serializers.BaseServiceProjectLinkSerializer):
    class Meta(structure_serializers.BaseServiceProjectLinkSerializer.Meta):
        model = models.OracleServiceProjectLink
        view_name = 'oracle-spl-detail'
        extra_kwargs = {
            'service': {'lookup_field': 'uuid', 'view_name': 'oracle-detail'},
        }


class DeploySerializer(structure_serializers.BaseResourceSerializer):

    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='oracle-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='oracle-spl-detail',
        queryset=models.OracleServiceProjectLink.objects.all())

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = models.Deploy
        view_name = 'oracle-deploys-detail'
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + ('report',)
        read_only_fields = structure_serializers.BaseResourceSerializer.Meta.read_only_fields + ('report',)
