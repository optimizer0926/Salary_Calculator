# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('personnel', '0005_vacation_average_daily_earnings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bonus',
            name='description',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
