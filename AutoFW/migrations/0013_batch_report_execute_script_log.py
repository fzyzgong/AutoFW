# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0012_auto_20180330_1442'),
    ]

    operations = [
        migrations.CreateModel(
            name='Batch_Report',
            fields=[
                ('report_id', models.CharField(unique=True, max_length=50)),
                ('report_name', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('API_total', models.IntegerField()),
                ('pass_total', models.IntegerField()),
                ('fail_total', models.IntegerField()),
                ('skip_total', models.IntegerField()),
                ('execute_man', models.CharField(max_length=30)),
                ('execute_time', models.DateTimeField()),
                ('bak1', models.CharField(max_length=50)),
                ('bak2', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'batch_report',
            },
        ),
        migrations.CreateModel(
            name='Execute_Script_Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('log_api_name', models.CharField(unique=True, max_length=100)),
                ('log_execute_script', models.CharField(max_length=3000)),
                ('bak1', models.CharField(max_length=50)),
                ('status', models.CharField(default=None, max_length=50)),
                ('log_report_id', models.ForeignKey(to='AutoFW.Batch_Report', to_field=b'report_id')),
            ],
            options={
                'db_table': 'execute_script_log',
            },
        ),
    ]
