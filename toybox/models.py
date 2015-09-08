import datetime
import django

from django.db import models
from django.utils import timezone

#TODO create key value pair table for one off settings - max toys borrowed etc
#
class Config(models.Model):
    key = models.CharField(max_length=30, unique=True)
    value = models.CharField(max_length=100)
    help= models.CharField(max_length=1024, default="")

    def __unicode__(self):
        return self.key+" = "+self.value+"  ("+self.help+")"

    def __str__(self):
        return self.key+" = "+self.value+"  ("+self.help+")"


class MemberType(models.Model):
    YEARLY = 0
    BIANNUALLY = 2
    QUARTERLY = 3
    MONTHLY = 4

    MEMBER_PERIOD_CHOICES = (
        (YEARLY, 'Yearly'),
        (BIANNUALLY, 'Biannually'),
        (QUARTERLY, 'Quarterly'),
        (MONTHLY, 'Monthly'),
    )
    membership_period = models.IntegerField(default=YEARLY, choices=MEMBER_PERIOD_CHOICES)
    name = models.CharField(max_length=20)
    fee = models.DecimalField(decimal_places=2, max_digits=5)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

# loan type needs some thought, regarding missing pieces and the issue register
# loan period may not be needed, or set to zero if not fixed- change to loan_period_max ?
# Removed member type, a toy can have only one loan type so different member type doesn't make sense
# overdue fine - per week?



class LoanType(models.Model):
    name = models.CharField(max_length=20)
    loan_period_max = models.IntegerField(blank=True, null=True)
    loan_cost = models.DecimalField(decimal_places=2, max_digits=5)
    overdue_fine = models.DecimalField(decimal_places=2, max_digits=5)
    missing_piece_fine = models.DecimalField(decimal_places=2, max_digits=5)
    missing_piece_refund = models.DecimalField(decimal_places=2, max_digits=5)
    loan_deposit = models.DecimalField(decimal_places=2, max_digits=5)
    # member_type = models.ForeignKey(MemberType, null=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class ToyCategory(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

class Member(models.Model):
    # surname?
    name = models.CharField(max_length=100)
    partner = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=300)
    phone_number1 = models.CharField(max_length=12)
    phone_number2 = models.CharField(max_length=12, blank=True)
    email_address = models.EmailField(blank=True)
    volunteer = models.BooleanField('Active volunteer', default=False)
    potential_volunteer = models.BooleanField(default=False)
    committee_member = models.BooleanField('Current committee member', default=False)
    anniversary_date = models.DateField('Membership due', default = django.utils.timezone.now)
    balance = models.DecimalField('Balance', decimal_places=2, max_digits=6, default=0)
    active = models.BooleanField(default=True)
    type = models.ForeignKey(MemberType)
    join_date = models.DateField(null=True)

    # volunteer capacity - bitfield
    # roster days - bitfield
    # member notes/characteristics?

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def membership_due_soon(self):
        #TODO move magic value to config
        return timezone.now().date + datetime.timedelta(days=60) <= self.anniversary_date

    def is_current(self):
        #TODO move magic value to config
        return timezone.now().date()<self.anniversary_date
        #return timezone.now().date + datetime.timedelta(days=14) > self.anniversary_date


class Child(models.Model):
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    parent = models.ForeignKey(Member)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class ToyBrand(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name





class ToyPackaging(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

class IssueChoiceType:
    ISSUE_NONE = 0
    BROKEN_REPAIRABLE = 1
    BROKEN_NOT_REPAIRABLE = 2
    MINOR_MISSING_PIECE = 3
    MAJOR_MISSING_PIECE = 4
    WHOLE_TOY_MISSING = 5
    RETURNED_MISSING_PIECE = 6
    RETURNED_MISSING_TOY = 7
    REPAIRED = 8


    ISSUE_TYPE_CHOICES = (
        (ISSUE_NONE,'No Issue'),
        (BROKEN_REPAIRABLE, 'Broken repairable'),
        (BROKEN_NOT_REPAIRABLE, 'Broken not repairable'),
        (MINOR_MISSING_PIECE, 'Minor missing piece'),
        (MAJOR_MISSING_PIECE, 'Major missing piece'),
        (WHOLE_TOY_MISSING, 'Whole toy missing'),
        (RETURNED_MISSING_PIECE, 'Returned missing piece'),
        (RETURNED_MISSING_TOY, 'Returned missing toy'),
        (REPAIRED, 'Repaired'),
    )

# should there be a borrow register, what about the history of the toy, how popular is it?
# This is a report they are interested in.
# this would be instead of recording the member, due date etc in the toy record. Not sure about state.
class Toy(models.Model):
    AT_TOY_LIBRARY = 0
    BORROWED = 1
    NOT_IN_SERVICE = 2

    AVAILABLE = 0
    MAJOR_NOTABLE_ISSUE = 1
    BEING_REPAIRED = 2
    MISSING = 3
    RETIRED = 4

    # needs to be table??
    # this is covering two different states, condition and location - might want to think about this
    # toy_state,text, can_be_borrowed,listed,user_selectable<- or done by workflow

    TOY_STATE_CHOICES = (
        (AT_TOY_LIBRARY, 'At Toy Library'),
        (BORROWED, 'Borrowed'),
        (NOT_IN_SERVICE, 'Not Available')
    )

    TOY_NOT_IN_SERVICE_STATE_CHOICES = (
        (AVAILABLE, 'Available'),
        (MAJOR_NOTABLE_ISSUE, 'Major Notable Issue'),
        (BEING_REPAIRED, 'Being Repaired'),
        (MISSING, 'Missing'),
        (RETIRED, 'Retired'),
    )

    # def file(self, filename):
    #     url = "./%d.JPG" % (self.id,)
    #     return url

    code = models.CharField(max_length=10, blank=False, unique=True)
    description = models.CharField(max_length=200)
    brand = models.ForeignKey(ToyBrand)
    last_check = models.DateField('Date last checked', blank=True, null=True)
    last_stock_take = models.DateField(blank=True, null=True)
    member_loaned = models.ForeignKey(Member, blank=True, null=True, on_delete=models.SET_NULL)
    due_date = models.DateField(blank=True, null=True)
    borrow_date=models.DateField(blank=True, null=True)
    max_age = models.IntegerField(blank=True, null=True)
    min_age = models.IntegerField(blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    purchase_cost = models.DecimalField(blank=True,null=True, decimal_places=2, max_digits=5)
    num_pieces = models.IntegerField('Number of Pieces', default=1)
    storage_location = models.CharField(max_length=50)
    state = models.IntegerField(choices=TOY_STATE_CHOICES, default=AT_TOY_LIBRARY)
    availability_state = models.IntegerField(choices=TOY_NOT_IN_SERVICE_STATE_CHOICES, default=AVAILABLE)
    image = models.ImageField(upload_to="toy_images", null=True)  # need Pillow (pip install Pillow)
    category = models.ForeignKey(ToyCategory, null=True)
    packaging = models.ForeignKey(ToyPackaging, null=True)
    loan_type = models.ForeignKey(LoanType, null=True)
    #TODO this is linked to loan type and should be removed, also late_fee
    #fee = models.DecimalField(decimal_places=2, max_digits=3, default=0.5)
    issue_type = models.IntegerField(choices=IssueChoiceType.ISSUE_TYPE_CHOICES, default=IssueChoiceType.ISSUE_NONE)

    def __unicode__(self):
        return self.code

    def __str__(self):
        return self.description

    def admin_image(self):
        return u'<img src="%s" style="max-height:150px;" />' % self.image.url

    admin_image.allow_tags = True

    def borrow_toy(self, member, duration):
        self.member_loaned = member
        self.borrow_date = timezone.now()
        self.state = self.BORROWED
        self.due_date = timezone.now() + datetime.timedelta(days=duration*7)
        self.save()

    def return_toy(self):
        self.member_loaned=None
        self.state=self.AT_TOY_LIBRARY
        self.save()




    # def admin_image(self):
    #     return '<a href="/media/{0}"><img src="/media/{0}"></a>'.format(self.image)
    #     image_.allow_tags = True


class TempBorrowList(models.Model):
    member = models.ForeignKey(Member)
    toy = models.ForeignKey(Toy)

    def store(self, member, toy):
        self.member = member
        self.toy = toy
        self.save()


    def __unicode__(self):
        return self.toy.code+":"+self.member.name

    def __str__(self):
        return self.toy.code+":"+self.member.name

# fine associated with missing pieces etc? currently captured by loan type

#add none=0?
class Issue(models.Model):
    toy = models.ForeignKey(Toy)
    date_time = models.DateField('Issue reported date and time', auto_now_add=True)
    issue_type = models.IntegerField(choices=IssueChoiceType.ISSUE_TYPE_CHOICES, default=IssueChoiceType.ISSUE_NONE)
    member_involved = models.ForeignKey(Member)
    # issue here? volunteer_reporting = models.ForeignKey(Member)
    comment = models.CharField(max_length=1024)

    def __unicode__(self):
        return self.comment

    def __str__(self):
        return self.comment


class Transaction(models.Model):
    DONATION = 0
    BOND_REFUND = 1
    PETTY_CASH_ADJUSTMENT = 2
    FROM_BANK = 3
    CREDIT_ADJUSTMENT = 4
    CHARGE_REVERSAL = 5
    PAYMENT = 6
    MEMBERSHIP = 7
    HIRE_CHARGE = 8
    FEE = 9
    FINE = 10
    DEBIT_ADJUSTMENT = 11
    REFUND = 12
    TO_BANK = 13
    BOND = 14

    TRANSACTION_TYPE_CHOICES = (
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
    member = models.ForeignKey(Member, null=True, related_name='member_involved')
    volunteer_reporting = models.ForeignKey(Member, related_name='volunteer_reporting')
    toy = models.ForeignKey(Toy, null=True)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField('Transaction amount', decimal_places=2, max_digits=6, default=0)

    def __unicode__(self):
        return self.get_transaction_type_display()  # ????

    def __str__(self):
        return self.get_transaction_type_display()
