# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0023_project_case_case_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='script_info',
            name='script_case_id',
            field=models.ForeignKey(default='TBS_DL_Init', to='AutoFW.Project_Case'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='script_info',
            name='script_case_name',
            field=models.CharField(max_length=100),
        ),
    ]
