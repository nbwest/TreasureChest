from django import forms
from toybox.models import *


#################
# general helpers
def fragment_search(fragment):
    if fragment != '':
        return Member.objects.filter(name__contains=fragment)
    else:
        return []


#################
# Context helpers
def get_memsummary_context(mid):
    member = Member.objects.get(pk=mid)
    toys = Toy.objects.get(member=mid)
    context = {'member': member,
               'toys': toys}
    return context


def get_memsearch_context(request):
    possible_members = fragment_search(request.GET.get('member_name_frag', ''))
    context = {'members': possible_members}
    return context


##################
# Form classes
class MemberSearchForm(forms.Form):
    member_name_fragment = forms.CharField(label="Member Name", max_length=20)
