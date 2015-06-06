# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('toybox', '0002_auto_20150605_2238'),
    ]

    operations = [
        migrations.AlterField(
            model_name='toy',
            name='last_check',
            field=models.DateField(null=True, verbose_name=b'Date last checked', blank=True),
        ),
        migrations.AlterField(
            model_name='toy',
            name='last_stocktake',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='toy',
            name='max_age',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='toy',
            name='member',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='toybox.Member', null=True),
        ),
        migrations.AlterField(
            model_name='toy',
            name='min_age',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='toy',
            name='purchase_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
