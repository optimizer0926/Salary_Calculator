# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('personnel', '0002_auto_20150420_0659'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vacation',
            name='description',
        ),
    ]
