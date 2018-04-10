# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0021_auto_20180410_2054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='execute_script_log',
            name='log_api_name',
            field=models.CharField(max_length=100),
        ),
    ]
