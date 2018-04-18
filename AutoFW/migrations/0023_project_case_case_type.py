# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0022_auto_20180410_2130'),
    ]

    operations = [
        migrations.AddField(
            model_name='project_case',
            name='case_type',
            field=models.CharField(default=1, max_length=20),
            preserve_default=False,
        ),
    ]
