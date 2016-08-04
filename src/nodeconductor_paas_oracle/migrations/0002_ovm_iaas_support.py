# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('nodeconductor_paas_oracle', '0001_squashed_0007_change_support_requests'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deployment',
            name='db_arch_size',
            field=models.PositiveIntegerField(blank=True, help_text=b'Archive storage size in GB', null=True, validators=[django.core.validators.MinValueValidator(10), django.core.validators.MaxValueValidator(2048)]),
        ),
        migrations.AlterField(
            model_name='deployment',
            name='db_charset',
            field=models.CharField(blank=True, max_length=256, choices=[(b'AL32UTF8 - Unicode UTF-8 Universal Character Set', b'AL32UTF8 - Unicode UTF-8 Universal Character Set'), (b'AR8ISO8859P6 - ISO 8859-6 Latin/Arabic', b'AR8ISO8859P6 - ISO 8859-6 Latin/Arabic'), (b'AR8MSWIN1256 - MS Windows Code Page 1256 8-Bit Latin/Arabic', b'AR8MSWIN1256 - MS Windows Code Page 1256 8-Bit Latin/Arabic'), (b'Other - please specify in Addtional Data field.', b'Other - please specify in Addtional Data field.')]),
        ),
        migrations.AlterField(
            model_name='deployment',
            name='db_template',
            field=models.CharField(blank=True, max_length=256, choices=[(b'General Purpose', b'General Purpose'), (b'Data Warehouse', b'Data Warehouse')]),
        ),
        migrations.AlterField(
            model_name='deployment',
            name='db_type',
            field=models.PositiveSmallIntegerField(choices=[(1, b'RAC'), (2, b'Single Instance/ASM'), (3, b'Single Instance'), (4, b'No database')]),
        ),
        migrations.AlterField(
            model_name='deployment',
            name='db_version',
            field=models.CharField(blank=True, max_length=256, choices=[(b'11.2.0.4', b'11.2.0.4'), (b'12.1.0.2', b'12.1.0.2')]),
        ),
    ]
