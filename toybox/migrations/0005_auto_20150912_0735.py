# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toybox', '0004_auto_20150912_0631'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='deposit_fee',
            field=models.DecimalField(default=0, max_digits=5, decimal_places=2),
        ),
        migrations.AddField(
            model_name='member',
            name='membership_fee',
            field=models.DecimalField(default=0, max_digits=5, decimal_places=2),
        ),
    ]
