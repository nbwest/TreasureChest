# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toybox', '0002_shift'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shift',
            name='comment',
        ),
    ]
