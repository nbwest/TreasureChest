# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Child',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Config',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(unique=True, max_length=30)),
                ('value', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_time', models.DateField(auto_now_add=True, verbose_name=b'Issue reported date and time')),
                ('issue_type', models.IntegerField(default=0, choices=[(0, b'No Issue'), (1, b'Broken repairable'), (2, b'Broken not repairable'), (3, b'Minor missing piece'), (4, b'Major missing piece'), (5, b'Whole toy missing'), (6, b'Returned missing piece'), (7, b'Returned missing toy'), (8, b'Repaired')])),
                ('comment', models.CharField(max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='LoanType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('loan_period_max', models.IntegerField(null=True, blank=True)),
                ('loan_cost', models.DecimalField(max_digits=5, decimal_places=2)),
                ('overdue_fine', models.DecimalField(max_digits=5, decimal_places=2)),
                ('missing_piece_fine', models.DecimalField(max_digits=5, decimal_places=2)),
                ('missing_piece_refund', models.DecimalField(max_digits=5, decimal_places=2)),
                ('loan_deposit', models.DecimalField(max_digits=5, decimal_places=2)),
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
                ('email_address', models.EmailField(max_length=254, blank=True)),
                ('volunteer', models.BooleanField(default=False, verbose_name=b'Active volunteer')),
                ('potential_volunteer', models.BooleanField(default=False)),
                ('committee_member', models.BooleanField(default=False, verbose_name=b'Current committee member')),
                ('anniversary_date', models.DateField(default=django.utils.timezone.now, verbose_name=b'Membership due')),
                ('balance', models.DecimalField(default=0, verbose_name=b'Balance', max_digits=6, decimal_places=2)),
                ('active', models.BooleanField(default=True)),
                ('join_date', models.DateField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='MemberType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('membership_period', models.IntegerField(default=0, choices=[(0, b'Yearly'), (2, b'Biannually'), (3, b'Quarterly'), (4, b'Monthly')])),
                ('name', models.CharField(max_length=20)),
                ('fee', models.DecimalField(max_digits=5, decimal_places=2)),
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
                ('code', models.CharField(unique=True, max_length=10)),
                ('description', models.CharField(max_length=200)),
                ('last_check', models.DateField(null=True, verbose_name=b'Date last checked', blank=True)),
                ('last_stock_take', models.DateField(null=True, blank=True)),
                ('due_date', models.DateField(null=True, blank=True)),
                ('borrow_date', models.DateField(null=True, blank=True)),
                ('max_age', models.IntegerField(null=True, blank=True)),
                ('min_age', models.IntegerField(null=True, blank=True)),
                ('purchase_date', models.DateField(null=True, blank=True)),
                ('purchase_cost', models.DecimalField(null=True, max_digits=5, decimal_places=2, blank=True)),
                ('num_pieces', models.IntegerField(default=1, verbose_name=b'Number of Pieces')),
                ('storage_location', models.CharField(max_length=50)),
                ('state', models.IntegerField(default=0, choices=[(0, b'At Toy Library'), (1, b'Borrowed'), (2, b'Not Available')])),
                ('availability_state', models.IntegerField(default=0, choices=[(0, b'Available'), (1, b'Major Notable Issue'), (2, b'Being Repaired'), (3, b'Missing'), (4, b'Retired')])),
                ('image', models.ImageField(null=True, upload_to=b'toy_images')),
                ('issue_type', models.IntegerField(default=0, choices=[(0, b'No Issue'), (1, b'Broken repairable'), (2, b'Broken not repairable'), (3, b'Minor missing piece'), (4, b'Major missing piece'), (5, b'Whole toy missing'), (6, b'Returned missing piece'), (7, b'Returned missing toy'), (8, b'Repaired')])),
            ],
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
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_time', models.DateField(auto_now_add=True, verbose_name=b'Transaction event date and time')),
                ('transaction_type', models.IntegerField(choices=[(0, b'Donation'), (1, b'Bond Refund'), (2, b'Petty Cash Adjustment'), (3, b'From Bank'), (4, b'Credit Adjustment'), (5, b'Charge Reversal'), (6, b'Payment'), (7, b'Membership'), (8, b'Hire charge'), (9, b'Fee'), (10, b'Fine'), (11, b'Debit Adjustment'), (12, b'Refund'), (13, b'To Bank'), (14, b'Bond')])),
                ('amount', models.DecimalField(default=0, verbose_name=b'Transaction amount', max_digits=6, decimal_places=2)),
                ('member', models.ForeignKey(related_name='member_involved', to='toybox.Member', null=True)),
                ('toy', models.ForeignKey(to='toybox.Toy', null=True)),
                ('volunteer_reporting', models.ForeignKey(related_name='volunteer_reporting', to='toybox.Member')),
            ],
        ),
        migrations.AddField(
            model_name='toy',
            name='brand',
            field=models.ForeignKey(to='toybox.ToyBrand'),
        ),
        migrations.AddField(
            model_name='toy',
            name='category',
            field=models.ForeignKey(to='toybox.ToyCategory', null=True),
        ),
        migrations.AddField(
            model_name='toy',
            name='loan_type',
            field=models.ForeignKey(to='toybox.LoanType', null=True),
        ),
        migrations.AddField(
            model_name='toy',
            name='member_loaned',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='toybox.Member', null=True),
        ),
        migrations.AddField(
            model_name='toy',
            name='packaging',
            field=models.ForeignKey(to='toybox.ToyPackaging', null=True),
        ),
        migrations.AddField(
            model_name='tempborrowlist',
            name='toy',
            field=models.ForeignKey(to='toybox.Toy'),
        ),
        migrations.AddField(
            model_name='member',
            name='type',
            field=models.ForeignKey(to='toybox.MemberType'),
        ),
        migrations.AddField(
            model_name='issue',
            name='member_involved',
            field=models.ForeignKey(to='toybox.Member'),
        ),
        migrations.AddField(
            model_name='issue',
            name='toy',
            field=models.ForeignKey(to='toybox.Toy'),
        ),
        migrations.AddField(
            model_name='child',
            name='parent',
            field=models.ForeignKey(to='toybox.Member'),
        ),
    ]
