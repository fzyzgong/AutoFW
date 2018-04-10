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
                ('report_id', models.IntegerField()),
                ('report_name', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('API_total', models.IntegerField()),
                ('pass_total', models.IntegerField()),
                ('fail_total', models.IntegerField()),
                ('skip_total', models.IntegerField()),
                ('execute_man', models.CharField(max_length=30)),
                ('API_name', models.CharField(unique=True, max_length=100)),
                ('execute_log', models.CharField(max_length=1500)),
                ('execute_time', models.DateTimeField()),
                ('bak1', models.CharField(max_length=50)),
                ('bak2', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'batch_report',
            },
        ),
    ]
