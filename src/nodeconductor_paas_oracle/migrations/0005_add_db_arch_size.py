# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('nodeconductor_paas_oracle', '0004_remove_flavor_backend_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='deployment',
            name='db_arch_size',
            field=models.PositiveIntegerField(default=10, help_text=b'Archive storage size in GB', validators=[django.core.validators.MinValueValidator(10), django.core.validators.MaxValueValidator(2048)]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='deployment',
            name='db_size',
            field=models.PositiveIntegerField(help_text=b'Data storage size in GB', validators=[django.core.validators.MinValueValidator(10), django.core.validators.MaxValueValidator(2048)]),
        ),
    ]
