import os
import sys
project_dir = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_dir)
os.environ['DJANGO_SETTINGS_MODULE']='treasurechest.settings'

#import django
#django.setup()


from toybox.models import *

############
# Reset DB
from subprocess import call
manage_py = os.path.join(project_dir, "manage.py")
print "manage.py path: " + manage_py
call([manage_py, "flush", "--noinput"])
call([manage_py, "syncdb", "--noinput"])

############
# MemberType
mt_public = MemberType()
mt_public.membership_period='Yearly'
mt_public.name='Public'
mt_public.fee=30
mt_public.save()

mt_playgroup = MemberType
mt_playgroup.membership_period='Biannually'
mt_playgroup.name='Play Group'
mt_playgroup.fee=200
mt_playgroup.save()


############
# Loan Type
#????

############
# Member
m_johndoh = Member
m_johndoh.name = 'John Doh'
m_johndoh.partner = 'James Doh'
m_johndoh.address = '123 example ln, Hacket'
m_johndoh.phone_number1 = '0404 404 505'
m_johndoh.email_address = 'john@doughboy.net'
m_johndoh.potential_volunteer = True
m_johndoh.balance = '5.5'
m_johndoh.type = mt_public.pk
m_johndoh.save()
