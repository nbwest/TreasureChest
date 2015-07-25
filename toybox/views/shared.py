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
def get_memsummary_context(mid):
    member = Member.objects.get(pk=mid)
    toys = Toy.objects.get(member=mid)
    context = {'member': member,
               'toys': toys}
    return context

def handle_member_search(request):
    possible_members = None
    form = MemberSearchForm()
    if (request.method == "POST"):
        form = MemberSearchForm(request.POST)
        if form.is_valid():
            possible_members = fragment_search(form.cleaned_data['member_name_fragment'])
    elif (request.method == "GET"):
        member_id = request.GET.get('mid', '0')
        possible_members = Member.objects.filter(pk=member_id)
        if (possible_members.count() > 0):
            form = MemberSearchForm(initial={
                'member_name_fragment': possible_members[0].name
            })
    context = {'member_search_form': form,
               'members': possible_members}
    return context

def handle_member_summary(request):
    context = {}
    member_id = request.GET.get('mid', 0)
    if (member_id):
        member = get_object_or_404(Member, pk=member_id)
        children = Child.objects.filter(parent=member_id)
        context = {'member': member,
                   'children': children}
    return context

def handle_borrowed_toy_list(request):
    context = {}
    member_id = request.GET.get('mid', 0)
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
