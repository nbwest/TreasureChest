# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toybox', '0007_auto_20151012_2052'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='toyhistory',
            name='register_type',
        ),
        migrations.AddField(
            model_name='toyhistory',
            name='event_type',
            field=models.IntegerField(null=True, choices=[(0, b'New'), (3, b'Borrow'), (1, b'Return'), (2, b'Issue'), (4, b'Retired')]),
        ),
        migrations.AddField(
            model_name='toyhistory',
            name='transaction',
            field=models.ForeignKey(to='toybox.Transaction', null=True),
        ),
    ]
