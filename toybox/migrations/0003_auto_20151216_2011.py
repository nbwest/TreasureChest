# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('toybox', '0002_config_help'),
    ]

    operations = [
        migrations.CreateModel(
            name='ToyHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_time', models.DateTimeField(auto_now_add=True, verbose_name=b'Event date and time')),
                ('event_type', models.IntegerField(null=True, choices=[(0, b'Available'), (1, b'On Loan'), (2, b'Stocktake'), (3, b'To Be Repaired'), (4, b'Being Repaired'), (5, b'Retired')])),
                ('issue_type', models.IntegerField(default=0, choices=[(0, b'No Issue'), (1, b'Broken repairable'), (2, b'Broken not repairable'), (3, b'Minor missing piece'), (4, b'Major missing piece'), (5, b'Whole toy missing')])),
                ('issue_comment', models.CharField(max_length=200, null=True, blank=True)),
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
        migrations.RenameField(
            model_name='member',
            old_name='anniversary_date',
            new_name='membership_end_date',
        ),
        migrations.RenameField(
            model_name='toy',
            old_name='description',
            new_name='name',
        ),
        migrations.RemoveField(
            model_name='member',
            name='active',
        ),
        migrations.RemoveField(
            model_name='toy',
            name='availability_state',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='toy',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='volunteer_reporting',
        ),
        migrations.AddField(
            model_name='member',
            name='deposit_paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='toy',
            name='borrow_counter',
            field=models.IntegerField(default=0),
        ),
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
        migrations.AddField(
            model_name='transaction',
            name='balance',
            field=models.DecimalField(default=0, max_digits=6, decimal_places=2),
        ),
        migrations.AddField(
            model_name='transaction',
            name='comment',
            field=models.CharField(max_length=1024, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='transaction',
            name='complete',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='membertype',
            name='membership_period',
            field=models.IntegerField(default=365, choices=[(365, b'Yearly'), (183, b'Biannually')]),
        ),
        migrations.AlterField(
            model_name='toy',
            name='code',
            field=models.CharField(max_length=10),
        ),
        migrations.AlterField(
            model_name='toy',
            name='issue_type',
            field=models.IntegerField(default=0, choices=[(0, b'No Issue'), (1, b'Broken repairable'), (2, b'Broken not repairable'), (3, b'Minor missing piece'), (4, b'Major missing piece'), (5, b'Whole toy missing')]),
        ),
        migrations.AlterField(
            model_name='toy',
            name='state',
            field=models.IntegerField(default=0, choices=[(0, b'Available'), (1, b'On Loan'), (2, b'Stocktake'), (3, b'To Be Repaired'), (4, b'Being Repaired'), (5, b'Retired')]),
        ),
        migrations.AlterField(
            model_name='toy',
            name='storage_location',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='date_time',
            field=models.DateTimeField(auto_now_add=True, verbose_name=b'Transaction event date and time'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.IntegerField(choices=[(0, b'Donation'), (1, b'Member Credit'), (2, b'Member Deposit'), (3, b'Membership fee'), (4, b'Borrow Fee'), (5, b'Issue Fee'), (6, b'Overdue Fee'), (7, b'Member Debit'), (8, b'Credit Adjustment'), (9, b'Debit Adjustment'), (10, b'Bank Deposit'), (11, b'Deposit Refund')]),
        ),
        migrations.DeleteModel(
            name='Issue',
        ),
        migrations.AddField(
            model_name='toyhistory',
            name='member',
            field=models.ForeignKey(to='toybox.Member'),
        ),
        migrations.AddField(
            model_name='toyhistory',
            name='toy',
            field=models.ForeignKey(to='toybox.Toy'),
        ),
    ]
