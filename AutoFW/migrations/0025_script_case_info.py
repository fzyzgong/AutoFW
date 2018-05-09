# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0024_auto_20180420_1726'),
    ]

    operations = [
        migrations.CreateModel(
            name='Script_Case_Info',
            fields=[
                ('script_case_id', models.CharField(max_length=50, serialize=False, primary_key=True)),
                ('script_case_name', models.CharField(max_length=100)),
                ('execution_order', models.CharField(max_length=1000)),
                ('config', models.CharField(max_length=500)),
                ('creator', models.CharField(max_length=30)),
                ('status', models.CharField(default=None, max_length=50)),
                ('script_case_type', models.CharField(max_length=10)),
                ('remark', models.CharField(max_length=100)),
                ('script_case_module_name', models.ForeignKey(to='AutoFW.Project_Module', to_field=b'module_name')),
                ('script_case_project_name', models.ForeignKey(to='AutoFW.Project', to_field=b'project_name')),
            ],
            options={
                'db_table': 'script_case_info',
            },
        ),
    ]
