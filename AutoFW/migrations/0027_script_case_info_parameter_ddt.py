# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0026_case_execution_report_execute_case_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='script_case_info',
            name='parameter_ddt',
            field=models.CharField(default=1, max_length=1500),
            preserve_default=False,
        ),
    ]
