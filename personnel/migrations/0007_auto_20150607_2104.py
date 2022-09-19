# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('personnel', '0006_auto_20150517_1836'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='department',
            options={'verbose_name': '\u043e\u0442\u0434\u0435\u043b', 'verbose_name_plural': '\u043e\u0442\u0434\u0435\u043b\u044b'},
        ),
        migrations.AlterModelOptions(
            name='employee',
            options={'verbose_name': '\u0441\u043e\u0442\u0440\u0443\u0434\u043d\u0438\u043a', 'verbose_name_plural': '\u0441\u043e\u0442\u0440\u0443\u0434\u043d\u0438\u043a\u0438'},
        ),
        migrations.AlterModelOptions(
            name='position',
            options={'verbose_name': '\u0434\u043e\u043b\u0436\u043d\u043e\u0441\u0442\u044c', 'verbose_name_plural': '\u0434\u043e\u043b\u0436\u043d\u043e\u0441\u0442\u0438'},
        ),
        migrations.AlterModelOptions(
            name='sicktime',
            options={'verbose_name': '\u0431\u043e\u043b\u044c\u043d\u0438\u0447\u043d\u044b\u0439', 'verbose_name_plural': '\u0431\u043e\u043b\u044c\u043d\u0438\u0447\u043d\u044b\u0435'},
        ),
        migrations.AlterModelOptions(
            name='vacation',
            options={'verbose_name': '\u043e\u0442\u043f\u0443\u0441\u043a', 'verbose_name_plural': '\u043e\u0442\u043f\u0443\u0441\u043a\u0430'},
        ),
        migrations.AlterField(
            model_name='bonus',
            name='amount',
            field=models.DecimalField(max_digits=22, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='employee',
            name='permanent_bonus_amount',
            field=models.DecimalField(max_digits=22, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='position',
            name='wages',
            field=models.DecimalField(max_digits=22, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='sicktime',
            name='last_two_years_wages',
            field=models.DecimalField(max_digits=22, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='vacation',
            name='average_daily_earnings',
            field=models.DecimalField(max_digits=22, decimal_places=2),
            preserve_default=True,
        ),
    ]
