# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers
import nodeconductor.logging.loggers
import django_fsm
import nodeconductor.core.models
import django.db.models.deletion
import django.utils.timezone
import nodeconductor.core.fields
import django.core.validators
import model_utils.fields
import nodeconductor.core.validators


class Migration(migrations.Migration):

    replaces = [(b'nodeconductor_paas_oracle', '0001_initial'), (b'nodeconductor_paas_oracle', '0002_flavor'), (b'nodeconductor_paas_oracle', '0003_db_type_choices'), (b'nodeconductor_paas_oracle', '0004_remove_flavor_backend_id'), (b'nodeconductor_paas_oracle', '0005_add_db_arch_size'), (b'nodeconductor_paas_oracle', '0006_add_ssh_metadata'), (b'nodeconductor_paas_oracle', '0007_change_support_requests')]

    dependencies = [
        ('structure', '0035_settings_tags_and_scope'),
        ('taggit', '0002_auto_20150616_2121'),
        ('openstack', '0001_initial'),
        ('nodeconductor_jira', '0004_project_available_for_all'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deployment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('description', models.CharField(max_length=500, verbose_name='description', blank=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', nodeconductor.core.fields.UUIDField()),
                ('error_message', models.TextField(blank=True)),
                ('state', django_fsm.FSMIntegerField(default=1, help_text='WARNING! Should not be changed manually unless you really know what you are doing.', choices=[(1, 'Provisioning Scheduled'), (2, 'Provisioning'), (3, 'Online'), (4, 'Offline'), (5, 'Starting Scheduled'), (6, 'Starting'), (7, 'Stopping Scheduled'), (8, 'Stopping'), (9, 'Erred'), (10, 'Deletion Scheduled'), (11, 'Deleting'), (13, 'Resizing Scheduled'), (14, 'Resizing'), (15, 'Restarting Scheduled'), (16, 'Restarting')])),
                ('backend_id', models.CharField(max_length=255, blank=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('report', models.TextField(blank=True)),
                ('db_name', models.CharField(max_length=256)),
                ('db_size', models.PositiveIntegerField(help_text=b'Data storage size in GB', validators=[django.core.validators.MinValueValidator(10), django.core.validators.MaxValueValidator(2048)])),
                ('db_arch_size', models.PositiveIntegerField(help_text=b'Archive storage size in GB', validators=[django.core.validators.MinValueValidator(10), django.core.validators.MaxValueValidator(2048)])),
                ('db_type', models.PositiveSmallIntegerField(choices=[(1, b'RAC'), (2, b'Single Instance/ASM'), (3, b'Single Instance')])),
                ('db_version', models.CharField(max_length=256, choices=[(b'11.2.0.4', b'11.2.0.4'), (b'12.1.0.2', b'12.1.0.2')])),
                ('db_template', models.CharField(max_length=256, choices=[(b'General Purpose', b'General Purpose'), (b'Data Warehouse', b'Data Warehouse')])),
                ('db_charset', models.CharField(max_length=256, choices=[(b'AL32UTF8 - Unicode UTF-8 Universal Character Set', b'AL32UTF8 - Unicode UTF-8 Universal Character Set'), (b'AR8ISO8859P6 - ISO 8859-6 Latin/Arabic', b'AR8ISO8859P6 - ISO 8859-6 Latin/Arabic'), (b'AR8MSWIN1256 - MS Windows Code Page 1256 8-Bit Latin/Arabic', b'AR8MSWIN1256 - MS Windows Code Page 1256 8-Bit Latin/Arabic'), (b'Other - please specify in Addtional Data field.', b'Other - please specify in Addtional Data field.')])),
                ('user_data', models.TextField(blank=True)),
                ('key_name', models.CharField(max_length=50, blank=True)),
                ('key_fingerprint', models.CharField(max_length=47, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(nodeconductor.core.models.SerializableAbstractMixin, nodeconductor.core.models.DescendantMixin, nodeconductor.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Flavor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', nodeconductor.core.fields.UUIDField()),
                ('cores', models.PositiveSmallIntegerField(help_text=b'Number of cores in a VM')),
                ('ram', models.PositiveIntegerField(help_text=b'Memory size in MiB')),
                ('disk', models.PositiveIntegerField(help_text=b'Root disk size in MiB')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OracleService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', nodeconductor.core.fields.UUIDField()),
                ('available_for_all', models.BooleanField(default=False, help_text='Service will be automatically added to all customers projects if it is available for all')),
                ('customer', models.ForeignKey(to='structure.Customer')),
            ],
            options={
                'abstract': False,
            },
            bases=(nodeconductor.core.models.SerializableAbstractMixin, nodeconductor.core.models.DescendantMixin, nodeconductor.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OracleServiceProjectLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project', models.ForeignKey(to='structure.Project')),
                ('service', models.ForeignKey(to='nodeconductor_paas_oracle.OracleService')),
            ],
            options={
                'abstract': False,
            },
            bases=(nodeconductor.core.models.SerializableAbstractMixin, nodeconductor.core.models.DescendantMixin, nodeconductor.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.AddField(
            model_name='oracleservice',
            name='projects',
            field=models.ManyToManyField(related_name='oracle_services', through='nodeconductor_paas_oracle.OracleServiceProjectLink', to='structure.Project'),
        ),
        migrations.AddField(
            model_name='oracleservice',
            name='settings',
            field=models.ForeignKey(to='structure.ServiceSettings'),
        ),
        migrations.AddField(
            model_name='deployment',
            name='flavor',
            field=models.ForeignKey(related_name='+', to='nodeconductor_paas_oracle.Flavor'),
        ),
        migrations.AddField(
            model_name='deployment',
            name='service_project_link',
            field=models.ForeignKey(related_name='deployments', on_delete=django.db.models.deletion.PROTECT, to='nodeconductor_paas_oracle.OracleServiceProjectLink'),
        ),
        migrations.AddField(
            model_name='deployment',
            name='support_requests',
            field=models.ManyToManyField(related_name='_deployment_support_requests_+', to='nodeconductor_jira.Issue'),
        ),
        migrations.AddField(
            model_name='deployment',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='deployment',
            name='tenant',
            field=models.ForeignKey(related_name='+', to='openstack.Tenant'),
        ),
        migrations.AlterUniqueTogether(
            name='oracleserviceprojectlink',
            unique_together=set([('service', 'project')]),
        ),
        migrations.AlterUniqueTogether(
            name='oracleservice',
            unique_together=set([('customer', 'settings')]),
        ),
    ]
