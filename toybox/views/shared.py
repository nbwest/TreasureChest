from django import forms
from django.shortcuts import redirect
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

def handle_member_search(member_id, request):
    possible_members = None
    form = MemberSearchForm()
    if (request.method == "POST"):
        form = MemberSearchForm(request.POST)
        if form.is_valid():
            possible_members = fragment_search(form.cleaned_data['member_name_fragment'])
    elif (request.method == "GET" and member_id):
        possible_members = Member.objects.filter(pk=member_id)
        if (possible_members.count() > 0):
            form = MemberSearchForm(initial={
                'member_name_fragment': possible_members[0].name
            })
        else:
            redirect('..')
    context = {'member_search_form': form,
               'members': possible_members}
    return context


def handle_borrowed_toy_list(member_id):
    context = {}
    if (member_id):
        toys = Toy.objects.filter(member_loaned=member_id)
        context = {'toy_list': toys}
    return context

##################
# Form classes
class MemberSearchForm(forms.Form):
    member_name_fragment = forms.CharField(label="Member Name", max_length=20)
