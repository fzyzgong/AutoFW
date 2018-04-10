# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('AutoFW', '0016_auto_20180410_1608'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch_report',
            name='report_id',
            field=models.CharField(unique=True, max_length=50),
        ),
    ]
