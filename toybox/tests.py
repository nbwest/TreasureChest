import datetime
from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from .models import Member, MemberType

def addMember(name, anv_offset):
    t = MemberType.objects.create(  name        = 'private',
                                    fee         = 30,)
    t.save()
    m = Member.objects.create(  member_name     = name,
                                phone_number1   = '11 2222 3333',
                                address         = 'home',
                                type            = t,
                                aniversary_date = datetime.datetime.now() + datetime.timedelta(days=anv_offset))
    m.save()

class MemberSearchTestCase(TestCase):
    def setUp(self):
        addMember('John Doh', 30)
        addMember('John Smith', 30)
        addMember('Fred Smith', 30)
        addMember('Jane Doh', 30)
        
    def test_fragment_search_with_empty_fragment(self):
        """
        fragment_search should not return any results for 
        an empty fragment
        """
        response = self.client.get(reverse('toybox:member_search'))
        self.assertQuerysetEqual(response.context['member_names'], [])

    def test_fragment_search_with_no_match(self):
        """
        fragment_search should not return any results if 
        fragment doesn't match any names
        """
        response = self.client.get(reverse('toybox:member_search'), {'member_name_frag': 'foo'})
        self.assertQuerysetEqual(response.context['member_names'], [])
        
    def test_fragment_search_returns_all_matches(self):
        """
        fragment_search should return all matching names
        """
        response = self.client.get(reverse('toybox:member_search'), {'member_name_frag': 'John'})
        self.assertContains(response, 'John Doh')
        self.assertContains(response, 'John Smith')
         
    def test_fragment_search_returns_lastname_matches(self):
        """
        fragment_search should return all matches, including 
        matches in the middle of the name
        """
        response = self.client.get(reverse('toybox:member_search'), {'member_name_frag': 'Smith'})
        self.assertContains(response, 'Fred Smith')
        self.assertContains(response, 'John Smith')
         
