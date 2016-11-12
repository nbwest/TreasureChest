# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import datetime
import toybox.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Child',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_of_birth', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=30)),
                ('value', models.CharField(max_length=100)),
                ('value_type', models.IntegerField(default=0, choices=[(0, b'String'), (1, b'Number'), (2, b'Boolean')])),
                ('help', models.CharField(default=b'', max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('page', models.IntegerField(default=0, choices=[(0, b'Not Applicable'), (1, b'Login'), (2, b'Borrow'), (3, b'Return'), (4, b'Members'), (5, b'Toys'), (6, b'Transactions'), (7, b'Reports'), (8, b'Admin'), (9, b'Feedback')])),
                ('comment', models.CharField(default=b'', max_length=2048)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.ImageField(upload_to=toybox.models.image_file_name)),
                ('type', models.IntegerField(choices=[(0, b'Toy'), (1, b'Receipt'), (2, b'Instructions')])),
                ('primary', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('partner', models.CharField(max_length=100, blank=True)),
                ('address', models.CharField(max_length=300)),
                ('phone_number1', models.CharField(max_length=12)),
                ('phone_number2', models.CharField(max_length=12, blank=True)),
                ('email_address', models.EmailField(max_length=254)),
                ('volunteer', models.BooleanField(default=False, verbose_name=b'Active volunteer')),
                ('potential_volunteer', models.BooleanField(default=False)),
                ('committee_member', models.BooleanField(default=False, verbose_name=b'Current committee member')),
                ('membership_end_date', models.DateField(default=datetime.date.today, verbose_name=b'Membership due', blank=True)),
                ('balance', models.DecimalField(default=0, verbose_name=b'Balance', max_digits=6, decimal_places=2)),
                ('active', models.BooleanField(default=True)),
                ('join_date', models.DateField(auto_now_add=True)),
                ('bond_fee_paid', models.DecimalField(default=0, max_digits=5, decimal_places=2)),
                ('bond_refunded', models.DateField(null=True, verbose_name=b'Deposit refunded', blank=True)),
                ('bond_absorbed', models.DateField(null=True, verbose_name=b'Deposit absorbed', blank=True)),
                ('volunteer_capacity_wed', models.BooleanField(default=False)),
                ('volunteer_capacity_sat', models.BooleanField(default=False)),
                ('comment', models.CharField(max_length=1024, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='MemberType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('membership_period', models.IntegerField(default=365, choices=[(365, b'Yearly'), (183, b'Biannually')])),
                ('name', models.CharField(max_length=20)),
                ('fee', models.DecimalField(default=0, max_digits=5, decimal_places=2)),
                ('bond', models.DecimalField(default=0, max_digits=5, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='RecycledToyId',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('toy_id', models.CharField(max_length=6)),
            ],
        ),
        migrations.CreateModel(
            name='TempBorrowList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('member', models.ForeignKey(to='toybox.Member')),
            ],
        ),
        migrations.CreateModel(
            name='Toy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=10)),
                ('state', models.IntegerField(default=0, choices=[(0, b'Available'), (1, b'On Loan'), (2, b'Stocktake'), (3, b'To Be Repaired'), (4, b'Being Repaired'), (5, b'Retired'), (6, b'To Be Retired'), (7, b'Missing'), (8, b'To Be Cataloged')])),
                ('name', models.CharField(max_length=200)),
                ('last_check', models.DateField(null=True, verbose_name=b'Date last checked', blank=True)),
                ('last_stock_take', models.DateField(null=True, blank=True)),
                ('due_date', models.DateField(null=True, blank=True)),
                ('borrow_date', models.DateField(null=True, blank=True)),
                ('min_age', models.IntegerField(null=True, blank=True)),
                ('purchase_date', models.DateField(null=True, blank=True)),
                ('purchase_cost', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
                ('num_pieces', models.IntegerField(default=1, verbose_name=b'Number of Pieces')),
                ('parts_list', models.CharField(max_length=1024, null=True, blank=True)),
                ('storage_location', models.CharField(max_length=50, null=True, blank=True)),
                ('comment', models.CharField(max_length=1024, null=True, blank=True)),
                ('issue_type', models.IntegerField(default=0, choices=[(0, b'No Issue'), (1, b'Broken repairable'), (2, b'Broken not repairable'), (3, b'Minor missing piece'), (4, b'Major missing piece'), (5, b'Whole toy missing'), (6, b'Verified to retire')])),
                ('issue_comment', models.CharField(max_length=200, null=True, blank=True)),
                ('borrow_counter', models.IntegerField(default=0)),
                ('loan_cost', models.DecimalField(default=0.5, max_digits=5, decimal_places=2)),
                ('loan_bond', models.DecimalField(default=0.0, max_digits=5, decimal_places=2)),
            ],
            options={
                'permissions': (('retire_toy', 'Can retire toys'),),
            },
        ),
        migrations.CreateModel(
            name='ToyBrand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ToyCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('code_prefix', models.CharField(max_length=2)),
                ('next_code_number', models.PositiveSmallIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ToyHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_time', models.DateTimeField(verbose_name=b'Event date and time')),
                ('event_type', models.IntegerField(null=True, choices=[(0, b'Available'), (1, b'On Loan'), (2, b'Stocktake'), (3, b'To Be Repaired'), (4, b'Being Repaired'), (5, b'Retired'), (6, b'To Be Retired'), (7, b'Missing'), (8, b'To Be Cataloged')])),
                ('issue_type', models.IntegerField(default=0, choices=[(0, b'No Issue'), (1, b'Broken repairable'), (2, b'Broken not repairable'), (3, b'Minor missing piece'), (4, b'Major missing piece'), (5, b'Whole toy missing'), (6, b'Verified to retire')])),
                ('issue_comment', models.CharField(max_length=200, null=True, blank=True)),
                ('volunteer_reporting', models.CharField(max_length=60, null=True, blank=True)),
                ('member', models.ForeignKey(blank=True, to='toybox.Member', null=True)),
                ('toy', models.ForeignKey(to='toybox.Toy')),
            ],
        ),
        migrations.CreateModel(
            name='ToyPackaging',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ToyVendor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_time', models.DateTimeField(auto_now_add=True, verbose_name=b'Transaction event date and time')),
                ('volunteer_reporting', models.CharField(max_length=60, null=True, blank=True)),
                ('transaction_type', models.IntegerField(choices=[(0, b'Donation'), (1, b'Member Credit'), (2, b'Member Bond'), (3, b'Membership fee'), (4, b'Borrow Fee'), (5, b'Issue Fee'), (6, b'Late Fee'), (7, b'Member Debit'), (8, b'Credit Adjustment'), (9, b'Debit Adjustment'), (10, b'Bank Deposit'), (11, b'Member Bond Refund'), (12, b'Payment'), (13, b'Change'), (14, b'Loan Bond'), (15, b'Loan Bond Refund')])),
                ('amount', models.DecimalField(default=0, verbose_name=b'Transaction amount', max_digits=6, decimal_places=2)),
                ('balance', models.DecimalField(default=0, max_digits=6, decimal_places=2)),
                ('comment', models.CharField(max_length=1024, null=True, blank=True)),
                ('complete', models.BooleanField(default=False)),
                ('member', models.ForeignKey(related_name='member_involved', to='toybox.Member', null=True)),
            ],
            options={
                'get_latest_by': 'date_time',
                'permissions': (('transaction_actions', 'Can bank and adjust till'),),
            },
        ),
        migrations.AddField(
            model_name='toyhistory',
            name='transaction',
            field=models.ForeignKey(related_name='toyhistory', blank=True, to='toybox.Transaction', null=True),
        ),
        migrations.AddField(
            model_name='toy',
            name='brand',
            field=models.ForeignKey(blank=True, to='toybox.ToyBrand', null=True),
        ),
        migrations.AddField(
            model_name='toy',
            name='category',
            field=models.ForeignKey(to='toybox.ToyCategory', null=True),
        ),
        migrations.AddField(
            model_name='toy',
            name='image',
            field=models.ForeignKey(to='toybox.Image', null=True),
        ),
        migrations.AddField(
            model_name='toy',
            name='image_instructions',
            field=models.ForeignKey(related_name='image_instruction_set', blank=True, to='toybox.Image', null=True),
        ),
        migrations.AddField(
            model_name='toy',
            name='image_receipt',
            field=models.ForeignKey(related_name='image_reciept_set', blank=True, to='toybox.Image', null=True),
        ),
        migrations.AddField(
            model_name='toy',
            name='member_loaned',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='toybox.Member', null=True),
        ),
        migrations.AddField(
            model_name='toy',
            name='packaging',
            field=models.ForeignKey(blank=True, to='toybox.ToyPackaging', null=True),
        ),
        migrations.AddField(
            model_name='toy',
            name='purchased_from',
            field=models.ForeignKey(to='toybox.ToyVendor', null=True),
        ),
        migrations.AddField(
            model_name='tempborrowlist',
            name='toy',
            field=models.ForeignKey(to='toybox.Toy'),
        ),
        migrations.AddField(
            model_name='recycledtoyid',
            name='category',
            field=models.ForeignKey(to='toybox.ToyCategory'),
        ),
        migrations.AddField(
            model_name='member',
            name='type',
            field=models.ForeignKey(to='toybox.MemberType'),
        ),
        migrations.AddField(
            model_name='child',
            name='parent',
            field=models.ForeignKey(to='toybox.Member'),
        ),
    ]
