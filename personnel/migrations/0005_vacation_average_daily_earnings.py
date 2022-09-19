# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('personnel', '0004_employee_hired'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacation',
            name='average_daily_earnings',
            field=models.DecimalField(default=0, max_digits=8, decimal_places=2),
            preserve_default=False,
        ),
    ]
