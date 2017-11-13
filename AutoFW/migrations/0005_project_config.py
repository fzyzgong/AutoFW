# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0004_emp_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project_Config',
            fields=[
                ('ip', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('domain', models.CharField(max_length=200)),
                ('bak_field1', models.CharField(max_length=100)),
                ('bak_field2', models.CharField(max_length=100)),
                ('project_id', models.ForeignKey(to='AutoFW.Project', to_field=b'project_code')),
            ],
            options={
                'db_table': 'project_config',
            },
        ),
    ]
