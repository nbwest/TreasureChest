__author__ = 'fightingbeige'
from django.core.management.base import BaseCommand
from django.core.exceptions import MultipleObjectsReturned
from toybox.models import *
from datetime import datetime, date

import csv

# Named indexes into Members CSV
LAST_NAME = 0
FIRST_NAME = 1
ADDR_STREET = 2
ADDR_SUBURB = 3
ADDR_STATE = 4
ADDR_POSTCODE = 5
PHONE_AH = 6
PHONE_BH = 7
MEMBERSHIP_PD = 8
DEPOSIT_PD = 9
DATE_JND = 10
EMAIL = 11
VOL = 12
DAYS = 13
STOCKTAKE = 14
NUM_CHILDREN = 15
CHILDREN = 16

class Command(BaseCommand):
    help = 'Load data from csv\'s into the database'
    firstRun=True

    # Try all the examples of date formats used in the data
    # 1-Mar-15, 1/03/2015, 1/3/15, 03/01/2015
    def try_date(self, date_txt):
        for fmt in ('%d-%b-%y', '%d/%m/%Y', '%d/%m/%y', '%m/%d/%Y', '%Y'):
            try:
                date_obj = datetime.strptime(date_txt, fmt)
            except ValueError:
                pass
            else:
                break
        else:
            print "Unable to parse date: "+date_txt
            date_obj = None

        return date_obj

    # Convert strings to boolean
    def parse_bool(self, bstring):
        return bstring in ['yes', 'Yes', 'y', 'Y']

    def handle(self, *args, **options):
        with open('/Users/fightingbeige/Desktop/mtb_members_cleaned.csv', 'rb') as members_file:
           members_reader = csv.reader(members_file, delimiter=',', quotechar='"')
           annual_member = MemberType.objects.get(name = "private")
           next_year = date(date.today().year, 1, 1)  # 1st Jan next year

           for member in members_reader:

               # Skip header line
               if member.__str__().startswith("['LastName', 'FirstName'"):
                   continue

               first_name = member[FIRST_NAME].title()
               last_name = member[LAST_NAME].title()
               name = first_name+" "+last_name
               print "Processing "+name

               address = member[ADDR_STREET]+" "+ \
                           member[ADDR_SUBURB]+" "+ \
                           member[ADDR_STATE]+" "+ \
                           member[ADDR_POSTCODE]

               join_date = self.try_date(member[DATE_JND])
               if join_date is None:
                   print "Unable to parse joined date, or none set.  Setting joined to now"
                   join_date = date.today()

               try:
                   member_record, created = Member.objects.get_or_create(
                       name = name,
                       address = address,
                       phone_number1 = member[PHONE_AH],
                       email_address = member[EMAIL],
                       anniversary_date = next_year,
                       type = annual_member,
                   )

                   member_record.phone_number2 = member[PHONE_BH]
                   member_record.deposit_fee = member[DEPOSIT_PD]
                   member_record.potential_volunteer = False
                   member_record.volunteer = self.parse_bool(member[VOL])
                   member_record.join_date = join_date
                   member_record.save()

               except MultipleObjectsReturned:
                   print "Multiple entries found for "+name+".  Skipping."
                   continue

               if (created):
                   print "New member added."
               else:
                   print "Found existing record.  Member data updated."

               num_children = member[NUM_CHILDREN]
               if num_children != '':
                   for child in range(0, int(num_children)):
                       child_index = CHILDREN + (child * 2)

                       gender = Child.get_gender(member[child_index+1])
                       bday = self.try_date(member[child_index])
                       c, created = Child.objects.get_or_create(
                           date_of_birth = bday,
                           gender = gender,
                           parent = member_record
                       )
                       c.save()
                       if created:
                           print "Added "+name+"'s child ("+gender+") born "+bday.strftime('%d/%m/%Y')
