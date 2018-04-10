# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0016_auto_20180410_2038'),
    ]

    operations = [
        migrations.RenameField(
            model_name='execute_script_log',
            old_name='log_report_id',
            new_name='logs_report_id',
        ),
    ]
