# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toybox', '0003_auto_20150911_0654'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membertype',
            name='membership_period',
            field=models.IntegerField(default=0, choices=[(0, b'Yearly'), (2, b'Biannually')]),
        ),
        migrations.AlterField(
            model_name='toy',
            name='storage_location',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
