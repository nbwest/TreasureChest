# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toybox', '0002_config_help'),
    ]

    operations = [
        migrations.AddField(
            model_name='toy',
            name='comment',
            field=models.CharField(max_length=1024, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='toy',
            name='issue_comment',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='toy',
            name='code',
            field=models.CharField(max_length=10),
        ),
    ]
