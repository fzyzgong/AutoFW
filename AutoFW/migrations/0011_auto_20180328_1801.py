# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0010_auto_20171120_1439'),
    ]

    operations = [
        migrations.AddField(
            model_name='project_case',
            name='headers',
            field=models.CharField(default=1, max_length=1000),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='project_case',
            name='parameter',
            field=models.CharField(max_length=1500),
        ),
    ]
