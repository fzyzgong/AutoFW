# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0011_auto_20180328_1801'),
    ]

    operations = [
        migrations.RenameField(
            model_name='project_config',
            old_name='bak_field1',
            new_name='protocol',
        ),
        migrations.AddField(
            model_name='project_case',
            name='parameter_format',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
