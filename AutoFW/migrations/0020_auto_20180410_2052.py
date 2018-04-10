# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0019_execute_script_log'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='execute_script_log',
            name='bak2',
        ),
        migrations.RemoveField(
            model_name='execute_script_log',
            name='bak3',
        ),
        migrations.AddField(
            model_name='batch_report',
            name='bak2',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]
