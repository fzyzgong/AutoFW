# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0015_auto_20180410_1550'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='execute_script_log',
            name='bak2',
        ),
        migrations.AddField(
            model_name='execute_script_log',
            name='status',
            field=models.CharField(default=None, max_length=50),
        ),
    ]
