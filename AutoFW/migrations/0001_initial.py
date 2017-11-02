# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project_code', models.CharField(unique=True, max_length=20)),
                ('project_name', models.CharField(max_length=50)),
                ('PRI', models.CharField(max_length=10)),
                ('create_time', models.DateTimeField()),
                ('creator', models.CharField(max_length=20)),
                ('department', models.CharField(max_length=30)),
            ],
            options={
                'db_table': 'project',
            },
        ),
        migrations.CreateModel(
            name='Project_Module',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('module_id', models.CharField(max_length=20)),
                ('module_name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=100)),
                ('project', models.ForeignKey(to='AutoFW.Project', to_field=b'project_code')),
            ],
            options={
                'db_table': 'project_module',
            },
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=30)),
                ('password', models.CharField(max_length=100)),
                ('authority', models.CharField(max_length=20)),
                ('createtime', models.DateTimeField()),
                ('remark', models.CharField(max_length=100)),
                ('position', models.CharField(max_length=20)),
                ('gender', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'userinfo',
            },
        ),
    ]
