from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from nodeconductor.structure import models as structure_models


class OracleService(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='oracle_services', through='OracleServiceProjectLink')

    @classmethod
    def get_url_name(cls):
        return 'oracle'


class OracleServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(OracleService)

    @classmethod
    def get_url_name(cls):
        return 'oracle-spl'


class Flavor(structure_models.BaseServiceProperty):
    cores = models.PositiveSmallIntegerField(help_text='Number of cores in a VM')
    ram = models.PositiveIntegerField(help_text='Memory size in MiB')
    disk = models.PositiveIntegerField(help_text='Root disk size in MiB')


class Deployment(structure_models.Resource):

    class Charset:
        AL32UTF8 = 'AL32UTF8 - Unicode UTF-8 Universal Character Set'
        AR8ISO8859P6 = 'AR8ISO8859P6 - ISO 8859-6 Latin/Arabic'
        AR8MSWIN1256 = 'AR8MSWIN1256 - MS Windows Code Page 1256 8-Bit Latin/Arabic'
        OTHER = 'Other - please specify in Addtional Data field.'

        CHOICES = (
            (AL32UTF8, AL32UTF8),
            (AR8ISO8859P6, AR8ISO8859P6),
            (AR8MSWIN1256, AR8MSWIN1256),
            (OTHER, OTHER),
        )

    class Type:
        RAC = 1
        ASM = 2
        SINGLE = 3

        CHOICES = (
            (RAC, 'RAC'),
            (ASM, 'Single Instance/ASM'),
            (SINGLE, 'Single Instance'),
        )

    class Template:
        GENERAL = 'General Purpose'
        WAREHOUSE = 'Data Warehouse'

        CHOICES = (
            (GENERAL, GENERAL),
            (WAREHOUSE, WAREHOUSE),
        )

    class Version:
        V11 = '11.2.0.4'
        V12 = '12.1.0.2'

        CHOICES = ((V11, V11), (V12, V12))

    service_project_link = models.ForeignKey(
        OracleServiceProjectLink, related_name='deployments', on_delete=models.PROTECT)

    support_request = models.ForeignKey('nodeconductor_jira.Issue', related_name='+', null=True)
    tenant = models.ForeignKey('openstack.Tenant', related_name='+')
    flavor = models.ForeignKey(Flavor, related_name='+')
    report = models.TextField(blank=True)
    db_name = models.CharField(max_length=256)
    db_size = models.PositiveIntegerField(
        validators=[MinValueValidator(10), MaxValueValidator(2048)], help_text='Data storage size in GB')
    db_arch_size = models.PositiveIntegerField(
        validators=[MinValueValidator(10), MaxValueValidator(2048)], help_text='Archive storage size in GB')
    db_type = models.PositiveSmallIntegerField(choices=Type.CHOICES)
    db_version = models.CharField(max_length=256, choices=Version.CHOICES)
    db_template = models.CharField(max_length=256, choices=Template.CHOICES)
    db_charset = models.CharField(max_length=256, choices=Charset.CHOICES)
    user_data = models.TextField(blank=True)

    @property
    def db_version_type(self):
        return "%s %s" % (self.db_version, self.get_db_type_display())

    @property
    def flavor_info(self):
        flavor = self.flavor
        backend = self.get_backend()
        return "%s -- vCPUs: %d, RAM: %d GB, System Storage: %d GB" % (
            flavor.name,
            flavor.cores,
            backend.mb2gb(flavor.ram),
            backend.mb2gb(flavor.disk))

    @classmethod
    def get_url_name(cls):
        return 'oracle-deployments'
