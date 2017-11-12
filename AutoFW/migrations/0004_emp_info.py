# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0003_auto_20171103_1729'),
    ]

    operations = [
        migrations.CreateModel(
            name='Emp_Info',
            fields=[
                ('name', models.CharField(max_length=20)),
                ('birthday', models.DateTimeField()),
                ('email', models.CharField(unique=True, max_length=50)),
                ('phone_id', models.CharField(max_length=11)),
                ('position', models.CharField(max_length=30)),
                ('remark', models.CharField(max_length=50)),
                ('job_number', models.IntegerField(serialize=False, primary_key=True)),
                ('other', models.CharField(max_length=30)),
                ('user_id', models.ForeignKey(to='AutoFW.UserInfo', to_field=b'username')),
            ],
            options={
                'db_table': 'emp_info',
            },
        ),
    ]
