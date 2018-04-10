# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0017_auto_20180410_2045'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='execute_script_log',
            name='logs_report_id',
        ),
        migrations.DeleteModel(
            name='Execute_Script_Log',
        ),
    ]
