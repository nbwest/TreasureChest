# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toybox', '0004_toy_membership_receipt_reference'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='toy',
            name='membership_receipt_reference',
        ),
        migrations.AddField(
            model_name='member',
            name='membership_receipt_reference',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
    ]
