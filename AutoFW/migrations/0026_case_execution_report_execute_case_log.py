# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0025_script_case_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='Case_Execution_Report',
            fields=[
                ('report_id', models.CharField(unique=True, max_length=50)),
                ('report_name', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('case_total', models.IntegerField()),
                ('pass_total', models.IntegerField()),
                ('fail_total', models.IntegerField()),
                ('skip_total', models.IntegerField()),
                ('execute_man', models.CharField(max_length=30)),
                ('execute_time', models.DateTimeField()),
                ('bak1', models.CharField(max_length=50)),
                ('bak2', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'case_execution_report',
            },
        ),
        migrations.CreateModel(
            name='Execute_Case_Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('log_execute_case', models.CharField(max_length=3000)),
                ('status', models.CharField(default=None, max_length=50)),
                ('bak1', models.CharField(max_length=50)),
                ('log_API_id', models.ForeignKey(to='AutoFW.Project_Case')),
                ('log_case_id', models.ForeignKey(to='AutoFW.Script_Case_Info')),
                ('log_report_id', models.ForeignKey(to='AutoFW.Case_Execution_Report', to_field=b'report_id')),
            ],
            options={
                'db_table': 'execute_case_log',
            },
        ),
    ]
