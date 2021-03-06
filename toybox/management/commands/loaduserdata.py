from django.core.management.base import BaseCommand
from toybox.views.toys import estimate_borrow_cost
from django.core.exceptions import MultipleObjectsReturned
from toybox.models import *
from datetime import datetime, date, timedelta
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
            print "ERROR  |Unable to parse date: "+date_txt
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
        if toy_code == '' or toy_code == None:
            raise ValueError("Empty toy code or 'None' provided")
        m = re.search('^\s*([A-Z]{1,2})\d+\s*$', toy_code)
        if m:
            toy_code_prefix = m.group(1)
        else:
            raise ValueError("Unknown toy code %s" % toy_code)
        return ToyCategory.objects.get(code_prefix=toy_code_prefix)

    # Lots of typos in member names on toy sheets so try a fuzzy
    # match
    #def get_fuzzy_member(self, name):
   
    def load_members (self, members_file):
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
            'DEPOSIT_REFUNDED',
            'DATE_JND',
            'EMAIL',
            'VOL',
            'DAYS',
            'STOCKTAKE',
            'COMMENT',
            'NUM_CHILDREN',
        ]
        members_reader = csv.DictReader(members_file, fieldnames=members_file_column_names, restkey='CHILDREN', delimiter=',', quotechar='"')
        for member in members_reader:
            #try:
                first_name = member['FIRST_NAME'].title()
                last_name = member['LAST_NAME'].title()
                name = first_name+" "+last_name
                if name == " ":
                    continue

                print "INFO   |Processing "+name+" ("+member["MEMBERSHIP_PD"]+")"

                address = member['ADDR_STREET']+" "+ \
                          member['ADDR_SUBURB']+" "+ \
                          member['ADDR_STATE']+" "+ \
                          member['ADDR_POSTCODE']

                join_date = self.try_date(member['DATE_JND'])
                if join_date is None:
                    #print "Unable to parse joined date, or none set.  Setting joined to now"
                    join_date = date.today()

                # Parse membership end date
                m = re.search('^\s?(\d+)\s?$', member['MEMBERSHIP_PD'])
                if m:
                    membership_end_date = date(int(m.group(1))+1, 1, 1)
                else:
                    membership_end_date = date.today()

                try:
                    member_records = Member.objects.filter( name = name )
                    num_records = member_records.count()
                    created = False
                    if num_records > 1:
                        raise MultipleObjectsReturned
                    elif num_records == 1:
                        member_record = member_records[0]
                    else:
                        member_record = Member(name = name)
                        created = True

                    # Validate DpPd/Deposit Refunded/Absorbed
                    deposit = 0
                    bond_refunded = None
                    bond_absorbed = None
                    if member['DEPOSIT_PD']:
                        m = re.search('^\$?(\d+(\.\d+)?)$', member['DEPOSIT_PD'])
                        if m:
                            deposit = float(m.group(1))
                        elif member['DEPOSIT_PD'].upper() == 'R':
                            bond_refunded = self.try_date(member['DEPOSIT_REFUNDED'])
                            print "INFO   |    Deposit refunded "+bond_refunded.strftime('%d/%m/%Y')
                        elif member['DEPOSIT_PD'].upper() == 'A':
                            bond_absorbed = self.try_date(member['DEPOSIT_REFUNDED'])
                            print "INFO   |    Deposit absorbed "+bond_absorbed.strftime('%d/%m/%Y')
                        else:
                            print "ERROR  |Unable to determine deposit for "+ \
                            member_record.name+".  Setting to 0"

                    # If it's a new member, or more recent data (based on MEMBERSHIP_PD) populate
                    if created or membership_end_date > member_record.membership_end_date:
                        member_record.address = address
                        member_record.phone_number1 = member['PHONE_AH']
                        member_record.email_address = member['EMAIL']
                        member_record.membership_end_date = membership_end_date
                        member_record.type = annual_member
                        member_record.phone_number2 = member['PHONE_BH']
                        member_record.bond_fee_paid = deposit
                        member_record.bond_refunded = bond_refunded
                        member_record.bond_absorbed = bond_absorbed
                        member_record.potential_volunteer = False
                        member_record.volunteer = self.parse_bool(member['VOL'])
                        member_record.join_date = join_date
                        member_record.comment = member['COMMENT']
                        if membership_end_date > date.today():
                            member_record.active=True
                        else:
                            member_record.active=False

                        member_record.volunteer_capacity_wed=self.parse_contains(member['DAYS'],['WED','BOTH','EITHER','WEDNESDAY'])
                        # print member[DAYS] +"->"+str(member_record.volunteer_capacity_wed)
                        member_record.volunteer_capacity_sat=self.parse_contains(member['DAYS'],['SAT','BOTH','EITHER','SATURDAY'])
                        # print member[DAYS] +"->"+str(member_record.volunteer_capacity_sat)

                        member_record.save()

                        if (created):
                            print "INFO   |    New member added."
                        else:
                            print "INFO   |    Found existing record.  Member data updated."
                    else:
                        print "INFO   |    Old data.  Not updating"


                except MultipleObjectsReturned:
                    print "ERROR  |Multiple entries found for "+name+".  Skipping."
                    continue

                num_children = member['NUM_CHILDREN']
                if num_children != '':
                    children = member['CHILDREN']
                    for child in range(0, int(num_children)):
                        child_index = child * 2

                        #gender = Child.get_gender(children['child_index+1'])
                        try:
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
                                    print "INFO   |    Added "+name+"'s child born "+bday.strftime('%d/%m/%Y')
                        except IndexError: # Listed as having more children than data provided
                            continue       # Just add the data we have
            #except Exception as e:
            #    print "Exception processing: "+member.__str__()+": "+str(e)

    def load_toys (self, toys_file):
        # Identify the toys category by its toy_id prefix
        toys_file_column_names = [
            'CODE',
            'DESCRIPTION',
            'PURCHASED_FROM',
            'COST',
            'DATE',
            'NUM_PIECES',
            'FEE',
            'BORROWS',
            'PARTS_LIST',
            'NOTES',
            'STATUS',
            'BORROWED_BY',
            'BORROW_DATE',
            'DUE_DATE',
            'RECODE'  # should be the same code as at the start of the line
        ]
        try:
            toy_reader = csv.DictReader(toys_file, fieldnames=toys_file_column_names, delimiter=',', quotechar='"', restkey='OTHER')
        except csv.error as e:
            print "ERROR  |Issue Converting to Dict "+e.message



        for toy in toy_reader:

           # print toy

            try:
                code = toy['CODE']
                if code == None or code == '':
                    continue
                try:
                    category = self.get_category_from_code(code)
                except ValueError as e:
                    print "ERROR  |Unable to extract toy code prefix ("+code+"), skipping: "+str(e)
                    continue

                description = toy['DESCRIPTION']

                # Check for currently unused toy codes
                if description == '':
                    print "WARNING|Unused toy code: "+code
                    recycled_toy_id, created = RecycledToyId.objects.get_or_create(toy_id=code,
                                                                          category=category)
                    recycled_toy_id.save()
                    continue

                # Find or create toy record
                toy_records = Toy.objects.filter( code = code,
                                                  name = description)
                num_records = toy_records.count()
                created = False
                if num_records > 1:
                    raise MultipleObjectsReturned
                elif num_records == 1:
                    toy_record = toy_records[0]
                else:
                    toy_record = Toy(code = code)
                    toy_record.name = description
                    created = True

                # Add/Update the category
                toy_record.category = category

                # Add/Update purchase cost
                purchase_cost = None
                m = re.search('\$?([\d\.]+)', toy['COST'])
                if m:
                    purchase_cost = m.group(1)
                else:
                    print "ERROR  |Failed to extract purchase cost of "+code+" from "+toy['COST']
                    purchase_cost = 0
                toy_record.purchase_cost = purchase_cost

                # Add/Update vendor
                vendor = toy['PURCHASED_FROM']
                toy_vendor, created_vendor = ToyVendor.objects.get_or_create(
                    defaults={'name': vendor},
                    name__iexact = vendor
                )
                if created_vendor:
                    toy_vendor.save()
                    print "INFO   |    Added new toy vendor '"+str(toy_vendor)+"'"
                toy_record.purchased_from = toy_vendor

                # Add/Update purchase date
                purchase_date = self.try_date(toy['DATE'])
                toy_record.purchase_date = purchase_date

                # Add/Update number of pieces
                # default to 1 piece if not specified
                num_pieces = 1 if toy['NUM_PIECES'] == '' else int(toy['NUM_PIECES'])
                toy_record.num_pieces = num_pieces

                # Add/Update loan fee
                # Defaults to 1% of purchase cost rounded up to nearest $0.50
                loan_fee = estimate_borrow_cost (toy_record.purchase_cost)
                m = re.search('\$?\s?([\d\.]+)', toy['FEE'])
                if m:
                    loan_fee = float(m.group(1))
                toy_record.loan_cost = loan_fee
                toy_record.loan_deposit = 0

                # Add/Update number of borrows
                m = re.search('(\d)+\+?', toy['BORROWS'])
                borrows = 0
                if m:
                    borrows = int(m.group(1))
                toy_record.borrow_counter = borrows

                # Add/Update parts list
                toy_record.parts_list = toy['PARTS_LIST']

                # Add/Update notes
                toy_record.comment = toy['NOTES']

                # Add/Update toy status.  default to AVAILABLE
                toy_status = Toy.AVAILABLE
                status = toy['STATUS'].upper()
                if status == 'OUT':
                    toy_status = Toy.ON_LOAN
                elif status == 'MISSING':
                    toy_status = Toy.MISSING
                elif status == 'REPAIR CUPBOARD':
                    toy_status = Toy.TO_BE_REPAIRED
                elif status == 'REPAIR':
                    toy_status = Toy.BEING_REPAIRED
                elif status == 'NOT CATALOGUED':
                    toy_status = Toy.TO_BE_CATALOGED
                toy_record.state = toy_status

                # Add/Update current borrower
                # extract First initial (if present) and surname from J. Smith
                if toy_record.state == Toy.ON_LOAN:
                    borrowed_by = toy['BORROWED_BY']
                    m = re.search('([a-zA-Z]?)[\. ]{0,2}([-\' a-zA-Z]+)', borrowed_by)
                    if m:
                        initial = ''
                        if m.group(1):
                            initial = m.group(1)
                        try:
                            member_record = Member.objects.get(name__icontains = m.group(2),
                                                               name__istartswith = initial)
                            toy_record.member_loaned = member_record
                        except Member.DoesNotExist:
                            print "ERROR  |Ambiguous member name "+borrowed_by+" (member does not exist)"+ \
                                  ".  Leaving borrowed_by blank but adding name to notes."
                            toy_record.comment = toy_record.comment + "\n" +\
                                                 "Borrowed by: "+borrowed_by
                        except MultipleObjectsReturned:
                            print "ERROR  |Ambiguous member name "+borrowed_by+"(multiple members match)"+ \
                                  ".  Leaving borrowed_by blank but adding name to notes."
                            toy_record.comment = toy_record.comment + "\n" +\
                                                 "Borrowed by: "+borrowed_by
                    else:
                        print "ERROR  |Toy "+toy_record.code+\
                              " marked as out, but member name '"+ borrowed_by+"' didn't match"
                        toy_record.comment = toy_record.comment + "\n" +\
                                             "Borrowed by: "+borrowed_by


                    toy_record.borrow_date = self.try_date(toy["BORROW_DATE"])
                    if toy_record.borrow_date == None:
                        print "ERROR  |No borrow date, assuming 2 weeks if valid due date"

                    # Add/Update due date if toy is on loan
                    toy_record.due_date = self.try_date(toy["DUE_DATE"])

                    if toy_record.due_date == None:
                        print "ERROR  |No due date"

                    #assume 2 weeks borrow time if not available
                    if toy_record.borrow_date==None and toy_record.due_date != None:
                        toy_record.borrow_date=toy_record.due_date - timedelta(days=14)

                # Update the DB record
                toy_record.save()

                if (created):
                    print "INFO   |    New toy: "+code+" - "+description
                else:
                    print "INFO   |    Update toy: "+code

            except AttributeError as e:
                print "ERROR  |Exception loading toy "+toy['DESCRIPTION']+": "+str(e)
                raise

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
                    print "ERROR  |File not a toy image ("+file+"). Skipping"
                    continue


                # First try and find the toy.
                # If there is no associated toy, don't load the image
                try:
                    toy = Toy.objects.get(category=toy_category, code=toy_code)

                except Toy.DoesNotExist as e:
                    print "ERROR  |No associated toy record for image "+file_path+".  Skipping"
                    # TODO this currently leaves the image in the DB and media dir.
                    # What should we do with this?
                    continue

                except MultipleObjectsReturned:
                    print "ERROR  |Multiple toys found with code: "+toy_code+". Skipping"
                    continue

                # Add image to the DB and copy to the media directory
                try:
                    with open(file_path, 'rb') as file_handle:

                        # Get new file name for image
                        file_name = toy_code
                        if image_id:
                            file_name += "_"+str.lower(image_id)
                        file_name += "."+image_extension

                        print "INFO   |    Loading "+file_path+" as "+file_name+" for "+toy_code

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
                    print "ERROR  |Multiple image records found for: "+file+". Skipping"
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
            print "ERROR  |Unable to find callback for file "+file_path
            print "\n".join(read_lines)
            raise ValueError("No callback for "+file_path)

    def handle(self, *args, **options):
        file_paths = options['file']
        if len(file_paths) == 0:
            print "ERROR  |Must supply one or more valid files to load data from"
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
                print "ERROR  |Invalid file path: "+file_path
                continue

