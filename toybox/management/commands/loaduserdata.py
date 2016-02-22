from django.core.management.base import BaseCommand
from django.core.exceptions import MultipleObjectsReturned
from toybox.models import *
from datetime import datetime, date
import os.path
from django.core.files import File
import re
import csv

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
    
    def get_category_from_code(self, toy_code):
        try:
            if toy_code == '' or toy_code == None:
                raise ValueError("Empty toy code or 'None' provided")
            m = re.search('^([A-Z]{1,2})\d+$', toy_code)
            toy_code_prefix = m.group(1)
            return ToyCategory.objects.get(code_prefix=toy_code_prefix)
        except AttributeError as e:
            raise
   
    def load_members (self, members_file):
        next_year = date(date.today().year, 1, 1)  # 1st Jan next year
        annual_member = MemberType.objects.get(name = "Public")

        members_file_column_names = [
            'LAST_NAME',
            'FIRST_NAME',
            'ADDR_STREET',
            'ADDR_SUBURB',
            'ADDR_STATE',
            'ADDR_POSTCODE',
            'PHONE_AH',
            'PHONE_BH',
            'MEMBERSHIP_PD',
            'DEPOSIT_PD',
            'DATE_JND',
            'EMAIL',
            'VOL',
            'DAYS',
            'STOCKTAKE',
            'NUM_CHILDREN',
        ]
        members_reader = csv.DictReader(members_file, fieldnames=members_file_column_names, restkey='CHILDREN', delimiter=',', quotechar='"')
        for member in members_reader:
            try:
                first_name = member['FIRST_NAME'].title()
                last_name = member['LAST_NAME'].title()
                name = first_name+" "+last_name
                print "Processing "+name

                address = member['ADDR_STREET']+" "+ \
                          member['ADDR_SUBURB']+" "+ \
                          member['ADDR_STATE']+" "+ \
                          member['ADDR_POSTCODE']

                join_date = self.try_date(member['DATE_JND'])
                if join_date is None:
                    print "Unable to parse joined date, or none set.  Setting joined to now"
                    join_date = date.today()

                try:
                    member_record, created = Member.objects.get_or_create(
                        name = name,
                        address = address,
                        phone_number1 = member['PHONE_AH'],
                        email_address = member['EMAIL'],
                        membership_end_date = next_year,
                        type = annual_member,
                    )

                    member_record.phone_number2 = member['PHONE_BH']
                    member_record.deposit_fee = member['DEPOSIT_PD']
                    member_record.potential_volunteer = False
                    member_record.volunteer = self.parse_bool(member['VOL'])
                    member_record.join_date = join_date
                    member_record.active=True

                    member_record.volunteer_capacity_wed=self.parse_contains(member['DAYS'],['WED','BOTH','EITHER','WEDNESDAY'])
                    # print member[DAYS] +"->"+str(member_record.volunteer_capacity_wed)
                    member_record.volunteer_capacity_sat=self.parse_contains(member['DAYS'],['SAT','BOTH','EITHER','SATURDAY'])
                    # print member[DAYS] +"->"+str(member_record.volunteer_capacity_sat)

                    member_record.save()

                except MultipleObjectsReturned:
                    print "Multiple entries found for "+name+".  Skipping."
                    continue

                if (created):
                    print "New member added."
                else:
                    print "Found existing record.  Member data updated."

                num_children = member['NUM_CHILDREN']
                if num_children != '':
                    children = member['CHILDREN']
                    for child in range(0, int(num_children)):
                        child_index = child * 2

                        #gender = Child.get_gender(children['child_index+1'])
                        bday = self.try_date(children[child_index])
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

    def load_toys (self, toys_file):
        # Identify the toys category by its toy_id prefix
        toys_file_column_names = [
            'CODE',
            'DESCRIPTION',
            'PURCHASED_FROM',
            'COST',
            'DATE',
            'NUM_PIECES',
            'FEE'
        ]
        toy_reader = csv.DictReader(toys_file, fieldnames=toys_file_column_names, delimiter=',', quotechar='"')
        for toy in toy_reader:
            try:
                code = toy['CODE']
                try:
                    category = self.get_category_from_code(code)
                except Exception as e:
                    print "Unable to extract toy code prefix ("+code+"), skipping: "+str(e)
                    continue

                description = toy['DESCRIPTION']

                # Check for currently unused toy codes
                if description == '':
                    recycled_toy_id, created = RecycledToyId.objects.get_or_create(toy_id=code,
                                                                          category=category)
                    recycled_toy_id.save()
                    if created:
                        print "Toy code "+code+" unused.  Added to available toy codes for "+str(category)
                    continue

                purchase_cost = None
                m = re.search('\$?([\d\.]+)', toy['COST'])
                if m:
                    purchase_cost = m.group(1)
                vendor = toy['PURCHASED_FROM']
                toy_vendor, created = ToyVendor.objects.get_or_create(
                    defaults={'name': vendor},
                    name__iexact = vendor
                )
                if created:
                    toy_vendor.save()
                    print "Added new toy vendor '"+str(toy_vendor)+"'"
                purchase_date = self.try_date(toy['DATE'])

                # default to 1 piece if not specified
                num_pieces = 1 if toy['NUM_PIECES'] == '' else int(toy['NUM_PIECES'])

                # Extract load fee
                m = re.search('\$?\s?([\d\.]+)', toy['FEE'])
                if m:
                    loan_fee = m.group(1)
                try:
                    toy_record, created = Toy.objects.get_or_create(
                        code = code,
                        name = description,
                        purchased_from = toy_vendor,
                        purchase_cost = purchase_cost,
                        purchase_date = purchase_date,
                        num_pieces = num_pieces,
                        category = category
                    )
                    if loan_fee:
                        toy_record.loan_cost = loan_fee
                    toy_record.loan_deposit = 0
                    toy_record.save()

                except MultipleObjectsReturned:
                    print "Multiple objects found for "+description
                    continue

                if (created):
                    print "New toy added: "+description
                else:
                    print "Found existing record.  Update toy "+code

            except AttributeError as e:
                print "Exception loading toy "+toy['DESCRIPTION']+": "+str(e)

    @staticmethod
    def parse_image_name(file):
        m = re.search('^MTB[-_ ]*([A-Z]{1,2}) ?(\d+)[ ]?([A-Za-z]?).([jJ][pP][gG])$', file)
        if (m == None):
            return (None, None, None, None)

        toy_category = ToyCategory.objects.get(code_prefix=m.group(1))
        toy_number = m.group(2)
        toy_code = toy_category.code_prefix+toy_number
        image_id = m.group(3)
        image_extension = str.lower(m.group(4))
        return (toy_category, toy_code, image_id, image_extension)

    def load_toy_photos(self, photos_dir):
        for root, dirs, files in os.walk(photos_dir):
            for file in files:
                file_path = os.path.join(root, file)

                # Extract details from image name
                toy_category, toy_code, image_id, image_extension = Command.parse_image_name(file)
                if (toy_code == None):
                    print "File not a toy image ("+file+"). Skipping"
                    continue


                # First try and find the toy.
                # If there is no associated toy, don't load the image
                try:
                    toy = Toy.objects.get(category=toy_category, code=toy_code)

                except Toy.DoesNotExist as e:
                    print "No associated toy record for image "+file_path+".  Skipping"
                    # TODO this currently leaves the image in the DB and media dir.
                    # What should we do with this?
                    continue

                except MultipleObjectsReturned:
                    print "Multiple toys found with code: "+toy_code+". Skipping"
                    continue

                # Add image to the DB and copy to the media directory
                try:
                    with open(file_path, 'rb') as file_handle:

                        # Get new file name for image
                        file_name = toy_code
                        if image_id:
                            file_name += "_"+str.lower(image_id)
                        file_name += "."+image_extension

                        print "Loading "+file_path+" as "+file_name+" for "+toy_code

                        # Add the image to the DB and media directory
                        image, created = Image.objects.get_or_create(file=file_name,
                                                                     type=Image.TOY)
                        image.file.save(file_name,
                                        File(file_handle),
                                        save=True)

                    # Now associate the image with the toy
                    toy.image = image
                    toy.save()

                except MultipleObjectsReturned:
                    print "Multiple image records found for: "+file+". Skipping"
                    continue




    # Header lines used to identify type of data being loaded
    HEADER_FUNC = 0
    HEADER_MATCH = 1
    # TODO Change these to use regexes
    HEADERS = [
        (load_members, 'LastName,FirstName'),
        (load_toys, 'No.,Description,Purchased From'),
        (load_toys, 'No,Description,Purchased From'),
        (load_toys, 'Number,Description,Purchased From'),
    ]

    # Read up to first 5 lines of file and determine the type of data based
    # on data types configured in HEADERS.
    # NOTE. header line of file is consumed by this function, so no need
    # to strip it later
    def parse_header(self, file, file_path):
        read_lines = []
        for n in range(5):
            line = file.readline()
            read_lines.append(line)
            for data_type in self.HEADERS:
                if line.startswith(data_type[self.HEADER_MATCH]):
                    return data_type[self.HEADER_FUNC]
        else:
            print "Unable to find callback for file "+file_path
            print "\n".join(read_lines)
            raise ValueError("No callback for "+file_path)

    def handle(self, *args, **options):
        file_paths = options['file']
        if len(file_paths) == 0:
            print "Must supply one or more valid files to load data from"
            exit(1)

        for file_path in file_paths:
            # Check for dir of images
            if os.path.isdir(file_path):
                self.load_toy_photos(file_path)
            elif os.path.isfile(file_path):
                with open(file_path, 'rb') as data_file:
                    callback = self.parse_header(data_file, file_path)
                    callback(self, data_file)
            else:
                print "Invalid file path: "+file_path
                continue

