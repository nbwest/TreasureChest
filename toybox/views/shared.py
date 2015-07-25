from django import forms
from django.shortcuts import redirect, get_object_or_404, get_list_or_404
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

#def get_memsummary_context(member_id):
#    member = Member.objects.get(pk=mid)
#    #toys = Toy.objects.get(member=mid)
#    context = {'member': member}
#    return context

# Process requests for the member_search frame
def handle_member_search(request):
    form = MemberSearchForm()
    possible_members = None

    # Search pressed.  Validate form and get list of matching members
    if (request.method == "POST"):
        form = MemberSearchForm(request.POST)
        if form.is_valid():
            possible_members = fragment_search(form.cleaned_data['member_name_fragment'])
    # TODO, find a way to persist member_name_fragment across refresh
    elif (request.method == "GET"):
        pass

    context = {'member_search_form': form,
               'members': possible_members}
    return context

def handle_member_summary(request, member_id):
    context = {}
    if (member_id):
        member = get_object_or_404(Member, pk=member_id)
        children = Child.objects.filter(parent=member_id)
        context = {'member': member,
                   'children': children}
    return context

def handle_borrowed_toy_list(request, member_id):
    context = {}
    if (member_id):
        toys = Toy.objects.filter(member_loaned=member_id)
        context = {'toy_list': toys}
    return context

def handle_toy_search(request):
    form = ToySearchForm()
    toys = None
    if (request.method == "POST"):
        form = ToySearchForm(request.POST)
        if form.is_valid():
            toys = get_list_or_404(Toy,
                                   code__contains=form.cleaned_data['toy_id'])

    context = {'toy_search_form': form,
               'toys': toys}
    return context

##################
# Form classes
class MemberSearchForm(forms.Form):
    member_name_fragment = forms.CharField(label="Member", max_length=20)

class ToySearchForm(forms.Form):
    toy_id = forms.CharField(label="Toy ID", max_length=10)
