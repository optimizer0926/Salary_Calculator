# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('personnel', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sicktime',
            name='description',
        ),
        migrations.AddField(
            model_name='employee',
            name='insurance_experience',
            field=models.SmallIntegerField(default=0, choices=[(0, '\u041c\u0435\u043d\u0435\u0435 5 \u043b\u0435\u0442'), (1, '\u041e\u0442 5 \u0434\u043e 8 \u043b\u0435\u0442'), (2, '8 \u043b\u0435\u0442 \u0438 \u0431\u043e\u043b\u0435\u0435')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sicktime',
            name='last_two_years_wages',
            field=models.DecimalField(default=0, max_digits=8, decimal_places=2),
            preserve_default=False,
        ),
    ]
