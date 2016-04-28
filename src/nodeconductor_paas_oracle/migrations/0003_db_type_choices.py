# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodeconductor_paas_oracle', '0002_flavor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deployment',
            name='db_type',
            field=models.PositiveSmallIntegerField(choices=[(1, b'RAC'), (2, b'Single Instance/ASM'), (3, b'Single Instance')]),
        ),
        migrations.AlterField(
            model_name='deployment',
            name='db_version',
            field=models.CharField(max_length=256, choices=[(b'11.2.0.4', b'11.2.0.4'), (b'12.1.0.2', b'12.1.0.2')]),
        ),
    ]
