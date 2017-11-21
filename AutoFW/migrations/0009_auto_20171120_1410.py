# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0008_script_info'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='script_info',
            name='bak_2',
        ),
        migrations.AddField(
            model_name='script_info',
            name='script_project_name',
            field=models.ForeignKey(to='AutoFW.Project', default=1, to_field=b'project_name'),
            preserve_default=False,
        ),
    ]
