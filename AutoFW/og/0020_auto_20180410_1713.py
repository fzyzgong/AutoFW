# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0019_auto_20180410_1712'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='execute_script_log',
            name='log_report_id',
        ),
        migrations.DeleteModel(
            name='Batch_Report',
        ),
        migrations.DeleteModel(
            name='Execute_Script_Log',
        ),
    ]
