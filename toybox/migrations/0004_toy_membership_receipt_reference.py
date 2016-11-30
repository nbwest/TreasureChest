# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toybox', '0003_remove_shift_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='toy',
            name='membership_receipt_reference',
            field=models.CharField(max_length=64, null=True, blank=True),
        ),
    ]
