# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0009_auto_20171120_1410'),
    ]

    operations = [
        migrations.RenameField(
            model_name='script_info',
            old_name='bak_1',
            new_name='script_status',
        ),
    ]
