# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodeconductor_paas_oracle', '0002_ovm_iaas_support'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deployment',
            name='db_name',
            field=models.CharField(max_length=256, blank=True),
        ),
    ]
