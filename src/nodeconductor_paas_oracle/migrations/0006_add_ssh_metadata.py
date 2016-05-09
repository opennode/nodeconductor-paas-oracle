# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodeconductor_paas_oracle', '0005_add_db_arch_size'),
    ]

    operations = [
        migrations.AddField(
            model_name='deployment',
            name='key_fingerprint',
            field=models.CharField(max_length=47, blank=True),
        ),
        migrations.AddField(
            model_name='deployment',
            name='key_name',
            field=models.CharField(max_length=50, blank=True),
        ),
    ]
