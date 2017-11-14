# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0006_project_config_port'),
    ]

    operations = [
        migrations.AddField(
            model_name='emp_info',
            name='salery',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='emp_info',
            name='work_year',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
