# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0015_remove_batch_report_bak3'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='batch_report',
            name='bak2',
        ),
        migrations.AddField(
            model_name='execute_script_log',
            name='bak3',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
    ]
