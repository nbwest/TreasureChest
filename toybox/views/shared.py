from django import forms
from django.shortcuts import redirect, get_object_or_404, get_list_or_404
from toybox.models import *
from django.forms import ModelChoiceField

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

    possible_members = None

    # Search pressed.  Validate form and get list of matching members
    if (request.method == "GET"):
        form = MemberSearchForm(request.GET)
        if form.is_valid():
            possible_members = fragment_search(form.cleaned_data['member_name_fragment'])
            form = MemberSearchForm(initial={"member_name_fragment":form.cleaned_data['member_name_fragment']})
    #
    # elif (request.method == "GET"):
    else:
         form = MemberSearchForm()


    context = {'member_search_form': form,
               'members': possible_members}
    # print(context)
    return context


def handle_member_summary(request, member_id):
    context = {}
    if (member_id):
        member = get_object_or_404(Member, pk=member_id)
        children = Child.objects.filter(parent=member_id)
        context = {'member': member.__dict__,'children': children}
        #print(context["member"])
    return context


def handle_toy_search(request):
    form = ToySearchForm()
    toys = None
    if (request.method == "POST"):
        form = ToySearchForm(request.POST)
        if form.is_valid():
            toys = get_list_or_404(Toy,code__contains=form.cleaned_data['toy_id'])

    context = {'toy_search_form': form,
               'toys': toys}
    return context


def handle_toy_summary(request):
    toy = None
    if (request.method == "GET" or
        request.method == "POST"):
        toycode = request.GET.get('tc')
        if (toycode):
            toy = get_object_or_404(Toy, code=toycode)

    context = {'toy': toy}
    return context


def get_members(*fields,**kwargs):
    return {"members":Member.objects.filter(kwargs).values(fields)}


def get_all_members_names():
     return {"members":Member.objects.values("name","id","phone_number1")}



##################
# Shared form classes
class MemberSearchForm(forms.Form):
    member_name_fragment = forms.CharField(label="Member Name", max_length=20)

class ToySearchForm(forms.Form):
    toy_id = forms.CharField(label="Toy ID", max_length=10)

