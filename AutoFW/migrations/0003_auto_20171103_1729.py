# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0002_auto_20171024_1438'),
    ]

    operations = [
        migrations.CreateModel(
            name='Project_Case',
            fields=[
                ('case_id', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('case_name', models.CharField(unique=True, max_length=30)),
                ('creator', models.CharField(max_length=20)),
                ('url_path', models.CharField(max_length=150)),
                ('method', models.CharField(max_length=20)),
                ('parameter', models.CharField(max_length=300)),
                ('expected', models.CharField(max_length=300)),
                ('description', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'project_case',
            },
        ),
        migrations.AlterField(
            model_name='project',
            name='project_name',
            field=models.CharField(unique=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='project_module',
            name='module_name',
            field=models.CharField(unique=True, max_length=50),
        ),
        migrations.AddField(
            model_name='project_case',
            name='module_name',
            field=models.ForeignKey(to='AutoFW.Project_Module', to_field=b'module_name'),
        ),
        migrations.AddField(
            model_name='project_case',
            name='project_name',
            field=models.ForeignKey(to='AutoFW.Project', to_field=b'project_name'),
        ),
    ]
