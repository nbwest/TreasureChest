# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toybox', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shift_date', models.DateField()),
                ('comment', models.CharField(default=b'', max_length=2048)),
                ('volunteer', models.ForeignKey(to='toybox.Member')),
            ],
        ),
    ]
