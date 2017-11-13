# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0005_project_config'),
    ]

    operations = [
        migrations.AddField(
            model_name='project_config',
            name='port',
            field=models.IntegerField(default=123),
            preserve_default=False,
        ),
    ]
