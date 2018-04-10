# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0018_auto_20180410_1711'),
    ]

    operations = [
        migrations.CreateModel(
            name='Execute_Script_Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('log_api_name', models.CharField(unique=True, max_length=100)),
                ('log_execute_script', models.CharField(max_length=3000)),
                ('bak1', models.CharField(max_length=50)),
                ('status', models.CharField(default=None, max_length=50)),
            ],
            options={
                'db_table': 'execute_script_log',
            },
        ),
        migrations.AlterField(
            model_name='batch_report',
            name='report_id',
            field=models.IntegerField(unique=True),
        ),
        migrations.AddField(
            model_name='execute_script_log',
            name='log_report_id',
            field=models.ForeignKey(to='AutoFW.Batch_Report', to_field=b'report_id'),
        ),
    ]
