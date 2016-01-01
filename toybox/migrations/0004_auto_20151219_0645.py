# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toybox', '0003_auto_20151216_2011'),
    ]

    operations = [
        migrations.AddField(
            model_name='membertype',
            name='deposit',
            field=models.DecimalField(default=0, max_digits=5, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='membertype',
            name='fee',
            field=models.DecimalField(default=0, max_digits=5, decimal_places=2),
        ),
    ]
