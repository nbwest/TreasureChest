# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toybox', '0005_auto_20150912_0735'),
    ]

    operations = [
        migrations.RenameField(
            model_name='toy',
            old_name='description',
            new_name='name',
        ),
    ]
