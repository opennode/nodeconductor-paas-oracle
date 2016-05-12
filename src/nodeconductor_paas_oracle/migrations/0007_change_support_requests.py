# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodeconductor_jira', '0004_project_available_for_all'),
        ('nodeconductor_paas_oracle', '0006_add_ssh_metadata'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deployment',
            name='support_request',
        ),
        migrations.AddField(
            model_name='deployment',
            name='support_requests',
            field=models.ManyToManyField(related_name='_deployment_support_requests_+', to='nodeconductor_jira.Issue'),
        ),
    ]
