# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toybox', '0006_auto_20150915_0717'),
    ]

    operations = [
        migrations.CreateModel(
            name='ToyHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_time', models.DateField(auto_now_add=True, verbose_name=b'Issue reported date and time')),
                ('register_type', models.IntegerField(choices=[(0, b'Borrow'), (1, b'Return'), (2, b'Issue')])),
                ('issue_type', models.IntegerField(default=0, choices=[(0, b'No Issue'), (1, b'Broken repairable'), (2, b'Broken not repairable'), (3, b'Minor missing piece'), (4, b'Major missing piece'), (5, b'Whole toy missing'), (6, b'Returned missing piece'), (7, b'Returned missing toy'), (8, b'Repaired')])),
                ('comment', models.CharField(max_length=1024)),
                ('member_involved', models.ForeignKey(to='toybox.Member')),
                ('toy', models.ForeignKey(to='toybox.Toy')),
                ('volunteer_reporting', models.ForeignKey(related_name='toyhistory_requests_created', to='toybox.Member')),
            ],
        ),
        migrations.RemoveField(
            model_name='issue',
            name='member_involved',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='toy',
        ),
        migrations.DeleteModel(
            name='Issue',
        ),
    ]
