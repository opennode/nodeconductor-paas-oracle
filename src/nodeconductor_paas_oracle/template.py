from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget

from rest_framework import serializers

from nodeconductor.core import models as core_models
from nodeconductor.openstack.models import Tenant
from nodeconductor.template.forms import ResourceTemplateForm
from nodeconductor.template.serializers import BaseResourceTemplateSerializer

from . import models


class OracleProvisionTemplateForm(ResourceTemplateForm):
    service = forms.ModelChoiceField(
        label="Oracle service", queryset=models.OracleService.objects.all(), required=False)

    tenant = forms.ModelChoiceField(label="Tenant", queryset=Tenant.objects.all(), required=False)
    flavor = forms.ModelChoiceField(label="Flavor", queryset=models.Flavor.objects.all(), required=False)
    ssh_public_key = forms.ModelChoiceField(
        label="SSH public key", queryset=core_models.SshPublicKey.objects.all(), required=False)

    db_size = forms.IntegerField(label='Data storage size', required=False)
    db_arch_size = forms.IntegerField(label='Archive storage size', required=False)
    db_type = forms.CharField(required=False)
    db_version = forms.CharField(required=False)
    db_template = forms.CharField(required=False)
    db_charset = forms.CharField(required=False)
    user_data = forms.CharField(label='User data', widget=AdminTextareaWidget(), required=False)

    class Meta(ResourceTemplateForm.Meta):
        fields = ResourceTemplateForm.Meta.fields + (
            'service', 'project', 'flavor', 'tenant',
            'db_size', 'db_arch_size', 'db_type', 'db_version', 'db_template', 'db_charset',
        )

    class Serializer(BaseResourceTemplateSerializer):
        service = serializers.HyperlinkedRelatedField(
            view_name='oracle-detail',
            queryset=models.OracleService.objects.all(),
            lookup_field='uuid',
            required=False,
        )
        flavor = serializers.HyperlinkedRelatedField(
            view_name='oracle-flavor-detail',
            lookup_field='uuid',
            queryset=models.Flavor.objects.all(),
            required=False,
        )
        tenant = serializers.HyperlinkedRelatedField(
            view_name='openstack-tenant-detail',
            lookup_field='uuid',
            queryset=Tenant.objects.all(),
            required=False,
        )
        ssh_public_key = serializers.HyperlinkedRelatedField(
            view_name='sshpublickey-detail',
            lookup_field='uuid',
            queryset=core_models.SshPublicKey.objects.all(),
            required=False,
        )
        db_size = serializers.IntegerField(required=False)
        db_arch_size = serializers.IntegerField(required=False)
        db_type = serializers.CharField(required=False)
        db_version = serializers.CharField(required=False)
        db_template = serializers.CharField(required=False)
        db_charset = serializers.CharField(required=False)
        user_data = serializers.CharField(required=False)

    @classmethod
    def get_serializer_class(cls):
        return cls.Serializer

    @classmethod
    def get_model(cls):
        return models.Deployment
