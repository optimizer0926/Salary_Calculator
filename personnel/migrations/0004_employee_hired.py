# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('personnel', '0003_remove_vacation_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='hired',
            field=models.DateField(default=datetime.date(2015, 1, 1)),
            preserve_default=False,
        ),
    ]
