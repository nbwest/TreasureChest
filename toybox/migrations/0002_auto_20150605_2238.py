# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toybox', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='toy',
            name='member',
            field=models.ForeignKey(to='toybox.Member', blank=True),
        ),
        migrations.AlterField(
            model_name='toy',
            name='name',
            field=models.CharField(max_length=60),
        ),
    ]
