from rest_framework import serializers

from nodeconductor.core import models as core_models
from nodeconductor.core import serializers as core_serializers
from nodeconductor.core.fields import NaturalChoiceField
from nodeconductor.structure import serializers as structure_serializers
from nodeconductor_openstack import models as openstack_models

from . import models


class ServiceSerializer(structure_serializers.BaseServiceSerializer):

    SERVICE_ACCOUNT_FIELDS = {
        'token': "JIRA project key (e.g. 'GM')"
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


class FlavorSerializer(structure_serializers.BasePropertySerializer):

    class Meta(object):
        model = models.Flavor
        view_name = 'oracle-flavors-detail'
        fields = ('url', 'uuid', 'name', 'cores', 'ram', 'disk')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class NestedFlavorSerializer(core_serializers.HyperlinkedRelatedModelSerializer, FlavorSerializer):

    class Meta(FlavorSerializer.Meta):
        pass


class DeploymentSerializer(structure_serializers.BaseResourceSerializer):

    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='oracle-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='oracle-spl-detail',
        queryset=models.OracleServiceProjectLink.objects.all())

    tenant = serializers.HyperlinkedRelatedField(
        view_name='openstack-tenant-detail',
        lookup_field='uuid',
        queryset=openstack_models.Tenant.objects.all(),
        write_only=True)

    flavor = serializers.HyperlinkedRelatedField(
        view_name='oracle-flavors-detail',
        lookup_field='uuid',
        queryset=models.Flavor.objects.all(),
        write_only=True)

    support_request = serializers.HyperlinkedRelatedField(
        view_name='jira-issues-detail',
        lookup_field='uuid',
        read_only=True)

    ssh_public_key = serializers.HyperlinkedRelatedField(
        view_name='sshpublickey-detail',
        lookup_field='uuid',
        queryset=core_models.SshPublicKey.objects.all(),
        required=False,
        write_only=True)

    db_type = NaturalChoiceField(choices=models.Deployment.Type.CHOICES)

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = models.Deployment
        view_name = 'oracle-deployments-detail'
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'tenant', 'flavor', 'ssh_public_key', 'support_request',
            'db_name', 'db_size', 'db_arch_size', 'db_type', 'db_version', 'db_template', 'db_charset',
            'user_data', 'report', 'key_name', 'key_fingerprint',
        )
        protected_fields = structure_serializers.BaseResourceSerializer.Meta.protected_fields + (
            'tenant', 'flavor', 'user_data', 'ssh_public_key',
            'db_name', 'db_size', 'db_arch_size', 'db_type', 'db_version', 'db_template', 'db_charset',
        )
        read_only_fields = structure_serializers.BaseResourceSerializer.Meta.read_only_fields + (
            'support_request', 'report', 'key_name', 'key_fingerprint',
        )

    def get_fields(self):
        fields = super(DeploymentSerializer, self).get_fields()
        if 'ssh_public_key' in fields:
            fields['ssh_public_key'].queryset = fields['ssh_public_key'].queryset.filter(
                user=self.context['request'].user)
        if self.instance:
            fields['flavor'] = NestedFlavorSerializer(read_only=True)
        return fields

    def validate(self, attrs):
        if attrs['service_project_link'].project != attrs['tenant'].service_project_link.project:
            raise serializers.ValidationError({'tenant': "Tenant and deployment projects don't match"})

        return attrs

    def create(self, validated_data):
        ssh_key = validated_data.pop('ssh_public_key', None)
        if ssh_key:
            validated_data['key_name'] = ssh_key.name
            validated_data['key_fingerprint'] = ssh_key.fingerprint

        return super(DeploymentSerializer, self).create(validated_data)


class DeploymentResizeSerializer(serializers.Serializer):

    flavor = serializers.HyperlinkedRelatedField(
        view_name='oracle-flavors-detail',
        lookup_field='uuid',
        queryset=models.Flavor.objects.all(),
        write_only=True)


class SupportSerializer(serializers.Serializer):
    message = serializers.CharField()
