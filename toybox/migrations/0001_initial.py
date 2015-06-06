# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('member_name', models.CharField(max_length=100)),
                ('partner_name', models.CharField(max_length=100, blank=True)),
                ('address', models.CharField(max_length=300)),
                ('phone_number1', models.CharField(max_length=12)),
                ('phone_number2', models.CharField(max_length=12, blank=True)),
                ('email_address', models.EmailField(unique=True, max_length=254, blank=True)),
                ('volunteer', models.BooleanField(default=False, verbose_name=b'Active volunteer')),
                ('potential_volunteer', models.BooleanField(default=False)),
                ('committee_member', models.BooleanField(default=False, verbose_name=b'Current committee member')),
                ('aniversary_date', models.DateField(verbose_name=b'Membership due')),
                ('balance', models.DecimalField(default=0, verbose_name=b'Balance owing', max_digits=6, decimal_places=2)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='MemberType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=20)),
                ('fee', models.DecimalField(max_digits=5, decimal_places=2)),
                ('membership_period', models.CharField(default=b'Y', max_length=1, choices=[(b'Y', b'Yearly'), (b'Q', b'Quaterly'), (b'M', b'Monthly')])),
            ],
        ),
        migrations.CreateModel(
            name='Toy',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=10)),
                ('description', models.CharField(max_length=200)),
                ('last_check', models.DateField(verbose_name=b'Date last checked', blank=True)),
                ('last_stocktake', models.DateField(blank=True)),
                ('max_age', models.IntegerField(blank=True)),
                ('min_age', models.IntegerField(blank=True)),
                ('purchase_date', models.DateField(blank=True)),
                ('num_pieces', models.IntegerField(default=1, verbose_name=b'Number of Pieces')),
                ('location', models.OneToOneField(to='toybox.Location')),
                ('member', models.ForeignKey(to='toybox.Member')),
            ],
        ),
        migrations.CreateModel(
            name='ToyBrand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='toy',
            name='toy_brand',
            field=models.OneToOneField(to='toybox.ToyBrand'),
        ),
        migrations.AddField(
            model_name='member',
            name='type',
            field=models.OneToOneField(to='toybox.MemberType'),
        ),
    ]
