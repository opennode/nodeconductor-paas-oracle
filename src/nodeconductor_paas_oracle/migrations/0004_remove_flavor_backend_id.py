# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodeconductor_paas_oracle', '0003_db_type_choices'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='flavor',
            name='backend_id',
        ),
    ]
