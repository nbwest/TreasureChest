import datetime

from django.db import models
from django.utils import timezone


class MemberType(models.Model):
    YEARLY = 0
    BIANNUALLY = 2
    QUARTERLY = 3
    MONTHLY = 4

    MEMBER_PERIOD_CHOICES = (
        (YEARLY, 'Yearly'),
        (BIANNUALLY, 'Bianually'),
        (QUARTERLY, 'Quarterly'),
        (MONTHLY, 'Monthly'),
    )

    name = models.CharField(max_length=20)
    fee = models.DecimalField(decimal_places=2, max_digits=5)
    membership_period = models.IntegerField(default=YEARLY, choices=MEMBER_PERIOD_CHOICES)

    def __unicode__(self):
        return self.name


class Member(models.Model):
    # surname?
    member_name = models.CharField(max_length=100)
    partner_name = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=300)
    phone_number1 = models.CharField(max_length=12)
    phone_number2 = models.CharField(max_length=12, blank=True)
    email_address = models.EmailField(blank=True)
    volunteer = models.BooleanField('Active volunteer', default=False)
    potential_volunteer = models.BooleanField(default=False)
    committee_member = models.BooleanField('Current committee member', default=False)
    anniversary_date = models.DateField('Membership due')
    balance = models.DecimalField('Balance owing', decimal_places=2, max_digits=6, default=0)
    active = models.BooleanField(default=True)
    type = models.ForeignKey(MemberType)
    join_date = models.DateField()

    # volunteer capacity - bitfield
    # roster days - bitfield
    # member notes/characteristics?

    def __unicode__(self):
        return self.member_name

    def membership_due_soon(self):
        return timezone.now().date + datetime.timedelta(days=60) <= self.aniversary_date


class Children(models.Model):
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField('Membership due')
    parent_member = models.ForeignKey(Member)

    def __unicode__(self):
        return self.name


class ToyBrand(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class StorageLocation(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class ToyCategory(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class ToyPackaging(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

class Toy(models.Model):
    AT_TOY_LIBRARY = 0
    BORROWED = 1
    MAJOR_NOTABLE_ISSUE = 2
    BEING_REPAIRED = 3
    MISSING = 4
    RETIRED = 5

    # needs to be table??
    # this is covering two different states, condition and location - might want to think about this
    # toy_state,text, can_be_borrowed,listed,user_selectable<- or done by workflow

    TOY_STATE_CHOICES = (
        (AT_TOY_LIBRARY, 'At Toy Library', True, True, False),
        (BORROWED, 'Borrowed', False, True, False),
        (MAJOR_NOTABLE_ISSUE, 'Major Notable Issue', False, True, False),
        (BEING_REPAIRED, 'Being Repaired', False, True, False),
        (MISSING, 'Missing', False, True, True),
        (RETIRED, 'Retired', False, False, True),
    )

    code = models.CharField(max_length=10, blank=False, unique=True)
    name = models.CharField(max_length=60, blank=False, unique=True)
    description = models.CharField(max_length=200)
    toy_brand = models.OneToOneField(ToyBrand)
    last_check = models.DateField('Date last checked', blank=True, null=True)
    last_stock_take = models.DateField(blank=True, null=True)
    member = models.ForeignKey(Member, blank=True, null=True, on_delete=models.SET_NULL)
    max_age = models.IntegerField(blank=True, null=True)
    min_age = models.IntegerField(blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    num_pieces = models.IntegerField('Number of Pieces', default=1)
    storage_location = models.OneToOneField(StorageLocation)
    state = models.IntegerField(choices=TOY_STATE_CHOICES)
    image = models.ImageField()
    category = models.ForeignKey(ToyCategory)
    packaging = models.ForeignKey(ToyPackaging)

    def __unicode__(self):
        return self.description


class IssuesResister(models.Model):
    BROKEN_REPAIRABLE = 0
    BROKEN_NOT_REPAIRABLE = 1
    MINOR_MISSING_PIECE = 2
    MAJOR_MISSING_PIECE = 3
    WHOLE_TOY_MISSING = 4
    RETURNED_MISSING_PIECE = 5
    REPAIRED = 6

    ISSUE_TYPE_CHOICES = (
        (BROKEN_REPAIRABLE, 'Broken repairable'),
        (BROKEN_NOT_REPAIRABLE, 'Broken not repairable'),
        (MINOR_MISSING_PIECE, 'Minor missing piece'),
        (MAJOR_MISSING_PIECE, 'Major missing piece'),
        (WHOLE_TOY_MISSING, 'Whole toy missing'),
        (RETURNED_MISSING_PIECE, 'Returned missing piece'),
        (REPAIRED, 'Repaired'),
    )
    toy = models.ForeignKey(Toy)
    date_time = models.DateField('Issue reported date and time', auto_now_add=True)
    issue_type = models.IntegerField(choices=ISSUE_TYPE_CHOICES)
    member_involved = models.ForeignKey(Member)
    volunteer_reporting = models.ForeignKey(Member)
    comment = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.comment


class TransactionRegister(models.Model):
    DONATION = 0,
    BOND_REFUND = 1,
    PETTY_CASH_ADJUSTMENT = 2,
    FROM_BANK = 3,
    CREDIT_ADJUSTMENT = 4,
    CHARGE_REVERSAL = 5,
    PAYMENT = 6,
    MEMBERSHIP = 7,
    HIRE_CHARGE = 8,
    FEE = 9,
    FINE = 10,
    DEBIT_ADJUSTMENT = 11,
    REFUND = 12,
    TO_BANK = 13,
    BOND = 14,

    ISSUE_TYPE_CHOICES = (
        (DONATION, 'Donation'),
        (BOND_REFUND, 'Bond Refund'),
        (PETTY_CASH_ADJUSTMENT, 'Petty Cash Adjustment'),
        (FROM_BANK, 'From Bank'),
        (CREDIT_ADJUSTMENT, 'Credit Adjustment'),
        (CHARGE_REVERSAL, 'Charge Reversal'),
        (PAYMENT, 'Payment'),
        (MEMBERSHIP, 'Membership'),
        (HIRE_CHARGE, 'Hire charge'),
        (FEE, 'Fee'),
        (FINE, 'Fine'),
        (DEBIT_ADJUSTMENT, 'Debit Adjustment'),
        (REFUND, 'Refund'),
        (TO_BANK, 'To Bank'),
        (BOND, 'Bond'),
    )
    date_time = models.DateField('Transaction event date and time', auto_now_add=True)
    volunteer_reporting = models.ForeignKey(Member)
    toy = models.ForeignKey(Toy)
    transaction_type = models.IntegerField(choices=ISSUE_TYPE_CHOICES)

    def __unicode__(self):
        return self.transaction_type
