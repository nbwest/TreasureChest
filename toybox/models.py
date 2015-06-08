import datetime

from django.db import models
from django.utils import timezone

MEMBER_PERIOD_CHOICES = (
    ('Y', 'Yearly'),
    ('Q', 'Quaterly'),
    ('M', 'Monthly'),
)

class MemberType(models.Model):
    name                = models.CharField(max_length=20)
    fee                 = models.DecimalField(decimal_places=2, max_digits=5)
    membership_period   = models.CharField(default='Y', max_length=1, choices=MEMBER_PERIOD_CHOICES)

    def __unicode__(self):
        return self.name

class Member(models.Model):
    member_name         = models.CharField(max_length=100)
    partner_name        = models.CharField(max_length=100, blank=True)
    address             = models.CharField(max_length=300)
    phone_number1       = models.CharField(max_length=12)
    phone_number2       = models.CharField(max_length=12, blank=True)
    email_address       = models.EmailField(blank=True)
    volunteer           = models.BooleanField('Active volunteer', default=False)
    potential_volunteer = models.BooleanField(default=False)
    committee_member    = models.BooleanField('Current committee member', default=False)
    aniversary_date     = models.DateField('Membership due')
    balance             = models.DecimalField('Balance owing', decimal_places=2, max_digits=6, default=0)
    active              = models.BooleanField(default=True)
    type                = models.ForeignKey(MemberType)

    def __unicode__(self):
        return self.member_name

    def membership_due_soon(self):
        return timezone.now().date + datetime.timedelta(days=60) <= self.aniversary_date 

class ToyBrand(models.Model):
    name                = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Location(models.Model):
    name                = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Toy(models.Model):
    name                = models.CharField(max_length=60)
    description         = models.CharField(max_length=200) 
    toy_brand           = models.OneToOneField(ToyBrand)
    last_check          = models.DateField('Date last checked', blank=True, null=True)
    last_stocktake      = models.DateField(blank=True, null=True)
    num_pieces          = models.IntegerField(default=1)
    member              = models.ForeignKey(Member, blank=True, null=True, on_delete=models.SET_NULL)
    max_age             = models.IntegerField(blank=True, null=True)
    min_age             = models.IntegerField(blank=True, null=True)
    purchase_date       = models.DateField(blank=True, null=True)
    num_pieces          = models.IntegerField('Number of Pieces', default=1)
    location            = models.OneToOneField(Location)

    def __unicode__(self):
        return self.description
