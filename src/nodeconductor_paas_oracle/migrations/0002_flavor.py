# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuidfield.fields
import nodeconductor.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('nodeconductor_paas_oracle', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flavor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(unique=True, max_length=255)),
                ('cores', models.PositiveSmallIntegerField(help_text=b'Number of cores in a VM')),
                ('ram', models.PositiveIntegerField(help_text=b'Memory size in MiB')),
                ('disk', models.PositiveIntegerField(help_text=b'Root disk size in MiB')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='deployment',
            name='flavor',
            field=models.ForeignKey(related_name='+', to='nodeconductor_paas_oracle.Flavor'),
        ),
    ]
