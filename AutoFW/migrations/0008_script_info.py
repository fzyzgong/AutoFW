# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0007_auto_20171114_1159'),
    ]

    operations = [
        migrations.CreateModel(
            name='Script_Info',
            fields=[
                ('script_name', models.CharField(max_length=100, serialize=False, primary_key=True)),
                ('script_path', models.CharField(max_length=200)),
                ('create_time', models.CharField(max_length=30)),
                ('bak_1', models.CharField(max_length=30)),
                ('bak_2', models.CharField(max_length=30)),
                ('remark', models.CharField(max_length=40)),
                ('script_case_name', models.ForeignKey(to='AutoFW.Project_Case', to_field=b'case_name')),
                ('script_module_name', models.ForeignKey(to='AutoFW.Project_Module', to_field=b'module_name')),
            ],
            options={
                'db_table': 'script_info',
            },
        ),
    ]
