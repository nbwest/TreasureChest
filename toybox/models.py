import datetime
import django
from datetime import date
from datetime import timedelta
from decimal import *

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Permission, User
import os.path


def thisDateTime():
    return timezone.make_aware(datetime.datetime.now(),timezone.get_default_timezone())

def format_username(user):

    if user.first_name=="":
        result= user.username
    else:
        result=user.first_name+" "+user.last_name
    return result


class Config(models.Model):

    STRING =0
    NUMBER=1
    BOOLEAN=2

    CONFIG_TYPES = (
        (STRING,"String"),
        (NUMBER,"Number"),
        (BOOLEAN,"Boolean"),
    )


    key = models.CharField(max_length=30, unique=True)
    value = models.CharField(max_length=100)
    value_type =  models.IntegerField(default=STRING, choices=CONFIG_TYPES)
    help = models.CharField(max_length=1024, default="")

    def __unicode__(self):
        return self.key + " = " + self.value + "  (" + self.help + ")"

    def __str__(self):
        return self.key + " = " + self.value + "  (" + self.help + ")"


class MemberType(models.Model):
    YEARLY = 365
    BIANNUALLY = 183
    # QUARTERLY = 13


    MEMBER_PERIOD_CHOICES = (
        (YEARLY, 'Yearly'),
        (BIANNUALLY, 'Biannually'),
        # (QUARTERLY, 'Quarterly'),
    )
    membership_period = models.IntegerField(default=YEARLY, choices=MEMBER_PERIOD_CHOICES)
    name = models.CharField(max_length=20)
    fee = models.DecimalField(decimal_places=2, max_digits=5,default=0)
    bond = models.DecimalField(decimal_places=2, max_digits=5, default=0)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class ToyCategory(models.Model):
    name = models.CharField(max_length=50)
    code_prefix = models.CharField(max_length=2)
    next_code_number = models.PositiveSmallIntegerField(default=0)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

class RecycledToyId(models.Model):
    toy_id = models.CharField(max_length=6)
    category = models.ForeignKey(ToyCategory)

    def __unicode__(self):
        return self.id

    def __str__(self):
        return self.id

class Member(models.Model):

    # surname?
    name = models.CharField(max_length=100)
    partner = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=300)
    phone_number1 = models.CharField(max_length=12)
    phone_number2 = models.CharField(max_length=12, blank=True)
    email_address = models.EmailField()
    volunteer = models.BooleanField('Active volunteer', default=False)
    potential_volunteer = models.BooleanField(default=False)
    committee_member = models.BooleanField('Current committee member', default=False)
    membership_end_date = models.DateField('Membership due', default=date.today, blank=True)
    balance = models.DecimalField('Balance', decimal_places=2, max_digits=6, default=0)
    active = models.BooleanField(default=True)
    type = models.ForeignKey(MemberType)
    join_date = models.DateField(auto_now_add=True, blank=True)
    bond_fee_paid = models.DecimalField(decimal_places=2, max_digits=5, default=0)
    bond_refunded = models.DateField('Deposit refunded', null=True, blank=True)
    bond_absorbed = models.DateField('Deposit absorbed', null=True, blank=True)
    volunteer_capacity_wed = models.BooleanField(default=False)
    volunteer_capacity_sat = models.BooleanField(default=False)
    comment = models.CharField(max_length=1024, blank=True)

    #TODO
    # roster days - bitfield
    # member notes/characteristics?


    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    # def membership_due_soon(self):
    #     # TODO move magic value to config
    #     return datetime.datetime.now().date + datetime.timedelta(days=60) <= self.membership_end_date

    def membership_valid(self):
        return (thisDateTime().now().date() < self.membership_end_date) or (self.type.fee==0)


    def bond_paid(self):
         return self.bond_fee_paid >0

    def is_current(self):
        return  self.membership_valid() and self.bond_paid()

    def update_membership_date(self):
        self.membership_end_date = thisDateTime().now().date()+timedelta(days=self.type.membership_period)
        self.save()




class Child(models.Model):

    date_of_birth = models.DateField()
    parent = models.ForeignKey(Member)

    def __unicode__(self):
        return str(self.date_of_birth)

    def __str__(self):
        return str(self.date_of_birth)


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

class ToyVendor(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name







def image_file_name(self, filename):
    return Image.image_path(filename, self.type)

class Image(models.Model):

    TOY = 0
    RECEIPT = 1
    INSTRUCTIONS = 2

    IMAGE_TYPE_CHOICES = (
        (TOY, "Toy"),
        (RECEIPT, "Receipt"),
        (INSTRUCTIONS, "Instructions")
    )
    # Separate images into subdirectories based on type
    @staticmethod
    def image_path (filename, type):
        dir = {
            Image.TOY: 'toys',
            Image.RECEIPT: 'receipts',
            Image.INSTRUCTIONS: 'instructions'
        }
        type_dir = dir[type]
        file_path = os.path.join("images", type_dir, filename)
        return file_path

    file = models.ImageField(upload_to=image_file_name)  # need Pillow (pip install Pillow)
    type = models.IntegerField(choices=IMAGE_TYPE_CHOICES)
    primary = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.file.name+" ["+self.IMAGE_TYPE_CHOICES[self.type][1]+"]")

    def __str__(self):
        return unicode(self.file.name+" ["+self.IMAGE_TYPE_CHOICES[self.type][1]+"]")

    def admin_image(self):
        if self.file != None:
            return u'<img src="%s" style="max-height:150px;image-orientation:from-image;" />' % self.file.url
        else:
            return "NO IMAGE"

    admin_image.allow_tags = True

class Toy(models.Model):
    AVAILABLE = 0
    ON_LOAN = 1
    STOCKTAKE = 2
    TO_BE_REPAIRED = 3
    BEING_REPAIRED = 4
    RETIRED = 5
    TO_BE_RETIRED = 6
    MISSING = 7
    TO_BE_CATALOGED = 8

    TOY_STATE_CHOICES = (
        (AVAILABLE, 'Available'),
        (ON_LOAN, 'On Loan'),
        (STOCKTAKE, 'Stocktake'),
        (TO_BE_REPAIRED, 'To Be Repaired'),
        (BEING_REPAIRED, 'Being Repaired'),
        (RETIRED, 'Retired'),
        (TO_BE_RETIRED, 'To Be Retired'),
        (MISSING, 'Missing'),
        (TO_BE_CATALOGED, 'To Be Cataloged'),
    )

    ISSUE_NONE = 0
    BROKEN_REPAIRABLE = 1
    BROKEN_NOT_REPAIRABLE = 2
    MINOR_MISSING_PIECE = 3
    MAJOR_MISSING_PIECE = 4
    WHOLE_TOY_MISSING = 5
    RETIRE_VERIFIED =6
    # not an issue, how would these been entered? - Not a "return" but noted in toy history?
    # RETURNED_MISSING_PIECE = 6
    # RETURNED_MISSING_TOY = 7





    ISSUE_TYPE_CHOICES = (
        (ISSUE_NONE, 'No Issue'),
        (BROKEN_REPAIRABLE, 'Broken repairable'),  # -> to admin cupboard
        (BROKEN_NOT_REPAIRABLE, 'Broken not repairable'),  # -> to be retired
        (MINOR_MISSING_PIECE, 'Minor missing piece'),  # -> to shelf
        (MAJOR_MISSING_PIECE, 'Major missing piece'),  # -> to admin cupboard
        (WHOLE_TOY_MISSING, 'Whole toy missing'),  # -> to be retired
        (RETIRE_VERIFIED, 'Verified to retire'),
        # who can retire a toy?
        # (RETURNED_MISSING_PIECE, 'Returned missing piece'),
        # (RETURNED_MISSING_TOY, 'Returned missing toy'),

    )

    #percentage of toy cost
    # ISSUE_FINE_MAJOR_MIN=Decimal(0.1)
    # ISSUE_FINE_MAJOR_MAX=Decimal(0.5)
    # ISSUE_FINE_MINOR_MIN=Decimal(0.1)
    # ISSUE_FINE_MINOR_MAX=Decimal(0.3)

    ISSUE_FINE_NONE =0
    ISSUE_FINE_MINOR =1
    ISSUE_FINE_MAJOR =2



    ISSUE_FINE_CHOICES = (
        (ISSUE_NONE, ISSUE_FINE_NONE),
        (BROKEN_REPAIRABLE, ISSUE_FINE_MINOR),
        (BROKEN_NOT_REPAIRABLE,ISSUE_FINE_MAJOR),
        (MINOR_MISSING_PIECE, ISSUE_FINE_MINOR),
        (MAJOR_MISSING_PIECE, ISSUE_FINE_MAJOR),
        (WHOLE_TOY_MISSING, ISSUE_FINE_MAJOR),
        (RETIRE_VERIFIED, ISSUE_FINE_NONE),
    )


    code = models.CharField(max_length=10, blank=False)
    state = models.IntegerField(choices=TOY_STATE_CHOICES, default=AVAILABLE)
    name = models.CharField(max_length=200)
    brand = models.ForeignKey(ToyBrand, null=True,blank=True )
    last_check = models.DateField('Date last checked', blank=True, null=True)
    last_stock_take = models.DateField(blank=True, null=True)
    member_loaned = models.ForeignKey(Member, blank=True, null=True, on_delete=models.SET_NULL)
    due_date = models.DateField(blank=True, null=True)
    borrow_date = models.DateField(blank=True, null=True)
    # max_age = models.IntegerField(blank=True, null=True)
    min_age = models.IntegerField(blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    purchase_cost = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=5)
    purchased_from = models.ForeignKey(ToyVendor, null=True)
    num_pieces = models.IntegerField('Number of Pieces', default=1)
    parts_list = models.CharField(blank=True, null=True, max_length=1024)
    storage_location = models.CharField(blank=True, null=True, max_length=50)

    image = models.ForeignKey(Image, null=True)
    image_receipt = models.ForeignKey(Image, related_name='image_reciept_set', null=True,blank=True)
    image_instructions = models.ForeignKey(Image, related_name='image_instruction_set', null=True,blank=True)

    category = models.ForeignKey(ToyCategory, null=True)
    packaging = models.ForeignKey(ToyPackaging, null=True,blank=True)

    comment = models.CharField(blank=True, null=True, max_length=1024)

    issue_type = models.IntegerField(choices=ISSUE_TYPE_CHOICES, default=ISSUE_NONE)
    issue_comment = models.CharField(blank=True, null=True, max_length=200)
    borrow_counter = models.IntegerField(default=0)
    
    loan_cost = models.DecimalField(decimal_places=2, max_digits=5, default=0.5)
    loan_bond = models.DecimalField(decimal_places=2, max_digits=5, default=0.0)


    @property
    def earned_back_cost(self):
        return (self.loan_cost * self.borrow_counter) >= self.purchase_cost

    @property
    def earned(self):
        return (self.loan_cost * self.borrow_counter)

    @property
    def issue_fine_major(self):

        from views.shared import get_config
        issue_fine_major_max=Decimal(get_config("major_issue_multiplier_max"))
        issue_fine_major_min=Decimal(get_config("major_issue_multiplier_min"))

        fine=(issue_fine_major_max * self.purchase_cost)-(self.loan_cost * self.borrow_counter)

        if fine<=0:
            fine=issue_fine_major_min * self.loan_cost

        fine=round(fine,0)

        return fine

    @property
    def issue_fine_minor(self):

        from views.shared import get_config
        issue_fine_minor_max=Decimal(get_config("minor_issue_multiplier_max"))
        issue_fine_minor_min=Decimal(get_config("minor_issue_multiplier_min"))

        fine=(issue_fine_minor_max * self.purchase_cost)-(self.loan_cost * self.borrow_counter)

        if fine<=0:
            fine=issue_fine_minor_min * self.loan_cost

        fine=round(fine,0)

        return fine

    @property
    def issue_fine_allocation(self):

        result=""
        for i in self.ISSUE_FINE_CHOICES:
            result=result+str(i[1])

        return result


    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


    def admin_image(self):
        if self.image != None:
            return u'<img src="%s" style="max-height:150px;image-orientation:from-image;" />' % self.image.file.url
        else:
            return "NO IMAGE"

    admin_image.allow_tags = True

    def borrow_toy(self, member, duration, user, loaned_for_repair, transaction, borrow_datetime):
        self.member_loaned = member
        self.borrow_date = borrow_datetime.date()

        if loaned_for_repair:
            self.state=self.BEING_REPAIRED
        else:
            self.state = self.ON_LOAN

        self.due_date = self.borrow_date + datetime.timedelta(days=duration * 7)
        self.save()

        toy_history=ToyHistory()
        toy_history.record_toy_event(self,user,borrow_datetime, transaction)


    def issue_type_to_state(self, issue_type):
        
        if issue_type == self.ISSUE_NONE:
            state = self.AVAILABLE
        elif issue_type == self.BROKEN_REPAIRABLE:
            state = self.TO_BE_REPAIRED
        elif issue_type == self.BROKEN_NOT_REPAIRABLE:
            state = self.TO_BE_RETIRED
        elif issue_type == self.MINOR_MISSING_PIECE:
            state = self.AVAILABLE
        elif issue_type == self.MAJOR_MISSING_PIECE:
            state = self.TO_BE_REPAIRED
        elif issue_type == self.WHOLE_TOY_MISSING:
            state = self.TO_BE_RETIRED
        elif issue_type == self.RETIRE_VERIFIED:
            state = self.RETIRED
            
        return state    

    def return_toy(self, issue, comment, user, return_datetime):

        self.issue_type = int(issue)

        self.state=self.issue_type_to_state(self.issue_type)

        self.issue_comment = comment

        toy_history=ToyHistory()
        toy_history.record_toy_event(self,user, return_datetime)

        self.member_loaned = None
        time_borrowed = return_datetime.date() - self.borrow_date
        self.borrow_counter += int(time_borrowed.days / 7)
        self.last_check = return_datetime

        self.save()

    # def change_toy_state(self, issue_type):
    #     if "retire_toy" in self.Meta.permissions:


    def weeks_overdue(self):

        if (self.due_date):
            monday2 = (thisDateTime().now().date() - timedelta(days=thisDateTime().now().date().weekday()))
            monday1 = (self.due_date - timedelta(days=self.due_date.weekday()))

            return (monday2 - monday1).days / 7
        else:
            return (0)


    def is_current(self):
        return thisDateTime().now().date() >= self.due_date

        # def admin_image(self):
        #     return '<a href="/media/{0}"><img src="/media/{0}"></a>'.format(self.image)
        #     image_.allow_tags = True

    class Meta:
        permissions = (
            ("retire_toy", "Can retire toys"),
        )


class TempBorrowList(models.Model):
    member = models.ForeignKey(Member)
    toy = models.ForeignKey(Toy)

    def store(self, member, toy):
        self.member = member
        self.toy = toy
        self.save()

    def __unicode__(self):
        return self.toy.code + ":" + self.member.name

    def __str__(self):
        return self.toy.code + ":" + self.member.name


class Transaction(models.Model):


    MEMBER_DONATION = 0 #+ From member to toy library. Automatic in Borrow page.
    MEMBER_CREDIT = 1   #+ From member to add to their credit amount. Added to till. Automatic from borrow page
    MEMBER_BOND = 2  #+ From member to toy library on membership sign up. Automatic from borrow page
    MEMBERSHIP_FEE = 3  #+ Member annual membership fee. Automatic from borrow page
    BORROW_FEE = 4      #+ Member borrows toy. Automatic from borrow page
    ISSUE_FEE = 5       #+ Member returns toy with notable issue. Automatic from returns page
    LATE_FEE = 6     #+ Member borrow overdue fee. Automatic from returns page
    MEMBER_DEBIT = 7    #0 Member uses credit to pay for fees, no money changes hands. Automatic from borrow page
    ADJUSTMENT_CREDIT = 8   #+ Adjustment of till. Manual from transactions page
    ADJUSTMENT_DEBIT = 9    #- Adjustment of till. Manual from transactions page
    BANK_DEPOSIT = 10       #- End of day take money to bank. Manual from transactions page
    MEMBER_BOND_REFUND = 11  #- From toy library to member once they cancel their the toy library membership. Manual from transaction page
    PAYMENT = 12
    CHANGE = 13
    LOAN_BOND = 14
    LOAN_BOND_REFUND = 15


    TRANSACTION_TYPE_CHOICES = (
    (MEMBER_DONATION,'Donation'),
    (MEMBER_CREDIT,'Member Credit'),
    (MEMBER_BOND,'Member Bond'),
    (MEMBERSHIP_FEE,'Membership fee'),
    (BORROW_FEE,'Borrow Fee'),
    (ISSUE_FEE,'Issue Fee'),
    (LATE_FEE,'Late Fee'),
    (MEMBER_DEBIT,'Member Debit'),
    (ADJUSTMENT_CREDIT,'Credit Adjustment'),
    (ADJUSTMENT_DEBIT,'Debit Adjustment'),
    (BANK_DEPOSIT,'Bank Deposit'),
    (MEMBER_BOND_REFUND,'Member Bond Refund'),
    (PAYMENT,'Payment'),
    (CHANGE,'Change'),
    (LOAN_BOND,'Loan Bond'),
    (LOAN_BOND_REFUND,'Loan Bond Refund')
    )



    date_time = models.DateTimeField('Transaction event date and time', auto_now_add=True)
    member = models.ForeignKey(Member, null=True, related_name='member_involved')
    volunteer_reporting = models.CharField(blank=True, null=True, max_length=60)
    transaction_type = models.IntegerField(choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField('Transaction amount', decimal_places=2, max_digits=6, default=0)
    balance = models.DecimalField(decimal_places=2, max_digits=6, default=0)
    comment = models.CharField(blank=True, null=True, max_length=1024)
    complete = models.BooleanField(default=False)

    def __unicode__(self):
        return self.get_transaction_type_display()  # ????

    def __str__(self):
        return self.get_transaction_type_display()


    def create_transaction_record(self, user,member, transaction_type, amount, comment=None, complete=True, balance_change=0.00):
        self.member = member

        self.transaction_type = transaction_type
        self.date_time = thisDateTime().now()
        self.comment = comment

        self.amount=amount
        self.complete=complete

        if Transaction.objects.count()>0:
            latest_transaction= Transaction.objects.last()
            # print "-------------------------------"
            #
            # print "TIMESTAMP : "+str(thisDateTime().now())
            # if member:
            #     print "MEMBER    : "+member.name
            # print "COMMENT   : "+str(comment)
            # print "TYPE      : "+Transaction.TRANSACTION_TYPE_CHOICES[transaction_type][1]
            # print "LAST B ID : "+str(latest_transaction.id)
            # print "LAST BAL  : "+str(latest_transaction.balance)
            # print "TR AMOUNT : "+str(amount)
            # print "BAL CHANGE: "+str(balance_change)

            self.balance = latest_transaction.balance + Decimal(balance_change)
            # print "NEW BAL   : "+str(self.balance)
            # print "COMPLETE  : "+str(complete)
        else:
            self.balance=balance_change


        self.volunteer_reporting=format_username(user)

        self.save()
        # print "ID        : "+str(self.id)


    class Meta:
        get_latest_by = "date_time"
        permissions = (
            ("transaction_actions", "Can bank and adjust till"),
        )



# fine associated with missing pieces etc? currently captured by loan type
# Issue register used for toy activity register as well
# add none=0?
class ToyHistory(models.Model):
    toy = models.ForeignKey(Toy)
    date_time = models.DateTimeField('Event date and time')
    event_type = models.IntegerField(choices=Toy.TOY_STATE_CHOICES, null=True)
    issue_type = models.IntegerField(choices=Toy.ISSUE_TYPE_CHOICES, default=Toy.ISSUE_NONE)
    issue_comment = models.CharField(blank=True, null=True, max_length=200)
    member = models.ForeignKey(Member, blank=True, null=True)
    volunteer_reporting = models.CharField(blank=True, null=True, max_length=60)
    transaction = models.ForeignKey(Transaction, null=True,blank=True,related_name="toyhistory" )

    def record_toy_event(self, toy, user, date_time, transaction=None):
        self.toy=toy
        self.date_time=date_time
        self.event_type=toy.state
        self.issue_comment=toy.issue_comment
        self.issue_type=toy.issue_type
        self.member=toy.member_loaned
        self.transaction=transaction


        self.volunteer_reporting= format_username(user)

        self.save()

    # def __unicode__(self):
    #     return self.date_time
    #
    # def __str__(self):
    #     return self.date_time

class Feedback(models.Model):

     NA=0
     LOGIN = 1
     BORROW = 2
     RETURN = 3
     MEMBERS = 4
     TOYS = 5
     TRANSACTIONS = 6
     REPORTS = 7
     ADMIN = 8
     FEEDBACK = 9


     PAGE_CHOICES = (
         (NA,"Not Applicable"),
         (LOGIN,"Login"),
         (BORROW,"Borrow"),
         (RETURN,"Return"),
         (MEMBERS,"Members"),
         (TOYS,"Toys"),
         (TRANSACTIONS,"Transactions"),
         (REPORTS,"Reports"),
         (ADMIN,"Admin"),
         (FEEDBACK,"Feedback")
     )

     name = models.CharField(max_length=60)
     date = models.DateTimeField(auto_now_add=True, blank=True)
     page = models.IntegerField(default=NA, choices=PAGE_CHOICES)
     comment = models.CharField(default="", max_length=2048)

     def __str__(self):
        return self.name + ": " + self.comment

class Shift(models.Model):

    shift_date = models.DateField()
    volunteer = models.ForeignKey(Member)

    def __unicode__(self):
        return str(self.shift_date)

    def __str__(self):
        return str(self.shift_date)