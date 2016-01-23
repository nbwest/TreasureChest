from django.core.management.base import BaseCommand
from django.core.exceptions import MultipleObjectsReturned
from toybox.models import *
from datetime import datetime, date
import os.path

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
    help = 'Load user data from csv\'s into the database'
    firstRun=True

    def add_arguments(self, parser):
        parser.add_argument('file', nargs='+', type=str)

    # Try all the examples of date formats used in the data
    # 1-Mar-15, 1/03/2015, 1/3/15, 03/01/2015
    def try_date(self, date_txt):
        for fmt in ('%d-%b-%y',
                    '%d/%m/%Y',
                    '%d.%m.%Y',
                    '%d/%m/%y',
                    '%d.%m.%y',
                    '%m/%d/%Y',
                    '%m.%d.%Y',
                    '%Y'):
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
        return bstring in ['yes', 'Yes', 'YES', 'y', 'Y']

    # def parse_wed(self, days):
    #
    #     if any(ext in days.upper() for ext in ['W','WED','BOTH','EITHER','WEDNESDAY']):
    #         return True
    #
    #     return False
    #
    # def parse_fri(self, days):
    #
    #     if any(ext in days.upper() for ext in ['F','FRI','BOTH','EITHER','FRIDAY']):
    #        return True
    #
    #     return False

    def parse_contains(self, source, string_list):

        if any(ext in source.upper() for ext in string_list):
           return True

        return False

    def load_members (self, members_file):
        next_year = date(date.today().year, 1, 1)  # 1st Jan next year
        annual_member = MemberType.objects.get(name = "Public")

        members_reader = csv.reader(members_file, delimiter=',', quotechar='"')
        for member in members_reader:
            try:
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
                        membership_end_date = next_year,
                        type = annual_member,
                    )

                    member_record.phone_number2 = member[PHONE_BH]
                    member_record.deposit_fee_paid = member[DEPOSIT_PD]
                    member_record.potential_volunteer = False
                    member_record.volunteer = self.parse_bool(member[VOL])
                    member_record.join_date = join_date

                    member_record.volunteer_capacity_wed=self.parse_contains(member[DAYS],['WED','BOTH','EITHER','WEDNESDAY'])
                    print member[DAYS] +"->"+str(member_record.volunteer_capacity_wed)
                    member_record.volunteer_capacity_sat=self.parse_contains(member[DAYS],['SAT','BOTH','EITHER','SATURDAY'])
                    print member[DAYS] +"->"+str(member_record.volunteer_capacity_sat)

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

                        #gender = Child.get_gender(member[child_index+1])
                        bday = self.try_date(member[child_index])
                        if (bday is not None):
                            c, created = Child.objects.get_or_create(
                                date_of_birth = bday,
                                #gender = gender,
                                parent = member_record
                            )
                            c.save()
                            if created:
                                #print "Added "+name+"'s child ("+gender+") born "+bday.strftime('%d/%m/%Y')
                                print "Added "+name+"'s child born "+bday.strftime('%d/%m/%Y')
            except Exception as e:
                print "Exception processing: "+member.__str__()+": "+str(e)

    # Header lines used to identify type of data being loaded
    HEADER_FUNC = 0
    HEADER_MATCH = 1
    HEADERS = [
        (load_members, 'LastName,FirstName'),
    ]

    # Read up to first 5 lines of file and determine the type of data based
    # on data types configured in HEADERS.
    # NOTE. header line of file is consumed by this function, so no need
    # to strip it later
    def parse_header(self, file):
        for n in range(5):
            line = file.readline()
            for data_type in self.HEADERS:
                if line.startswith(data_type[self.HEADER_MATCH]):
                    return data_type[self.HEADER_FUNC]
        else:
            return None

    def handle(self, *args, **options):
        file_paths = options['file']
        if len(file_paths) == 0:
            print "Must supply one or more valid files to load data from"
            exit(1)

        for file_path in file_paths:
            if not os.path.isfile(file_path):
                print "Invalid file path: "+file_path
                continue

            with open(file_path, 'rb') as data_file:
                callback = self.parse_header(data_file)
                callback(self, data_file)
