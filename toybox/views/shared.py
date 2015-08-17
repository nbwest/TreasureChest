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

    return context


def handle_member_summary(request, member_id):
    context = {}
    if (member_id):
        member = get_object_or_404(Member, pk=member_id)
        children = Child.objects.filter(parent=member_id)
        context = {'member': member.__dict__,'children': children}
        #print(context["member"])
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


def handle_returns(request,member_id):
    context={}

    context.update(handle_member_search(request))

    if (request.method == "GET"):
        if (member_id):
            context.update(handle_member_summary(request, member_id))

    return context


#TODO defines clear modes of operation with action
# POST - Guide: Use POST all the time except when you want the ability to bookmark a page, then use GET
#               Don't use GET to define actions
# GET
#/toybox/membership/ - display all members, clear form, submit button is "Add"
#/toybox/membership/1 - display all members, display member in form, submit button is "Update"
#/toybox/membership/?search=name_fragment - display search members, submit button is "Update"
#/toybox/membership/1/?search=name_fragment - display search members, submit button is "Update"


def handle_member_details(request, member_id):
    context={}

    context.update(handle_member_search(request))

    if (request.method == "GET"):

        if (context["members"]!=None) or (member_id):
            context.update({"member_detail_submit_button_label":"Update"})
        else:
            context.update({"member_detail_submit_button_label":"Add"})

        if (member_id):
            context.update(handle_member_summary(request, member_id))
            form = MemberAdminForm(initial=context["member"],label_suffix="")
        else:
            form = MemberAdminForm(label_suffix="")


    #if no members have been searched for display all members
    if context["members"]==None:
        context.update(get_all_members_names())


    context.update({'member_details_form': form})

    return context


##################
# Form classes
class MemberSearchForm(forms.Form):
    member_name_fragment = forms.CharField(label="Member", max_length=20)

class ToySearchForm(forms.Form):
    toy_id = forms.CharField(label="Toy ID", max_length=10)

class MemberAdminForm(forms.Form):
    name=forms.CharField(label="Name", max_length=Member._meta.get_field('name').max_length)
    phone_number1=forms.CharField(label="Phone Number", max_length=Member._meta.get_field('phone_number1').max_length)#Member.phone_number1.max_length)
    address=forms.CharField(label="Address", max_length=Member._meta.get_field('address').max_length)
    email_address=forms.CharField(label="Email", max_length=Member._meta.get_field('email_address').max_length)
    type=ModelChoiceField(queryset=MemberType.objects.all(),label="Member Type")
    committee_member=forms.BooleanField(label="Committee Member")
    volunteer = forms.BooleanField(label="Volunteer")





 #    partner = models.CharField(max_length=100, blank=True)
 #    potential_volunteer = models.BooleanField(default=False)
 #    # anniversary_date = models.DateField('Membership due',null=True)
 #    balance = models.DecimalField('Balance', decimal_places=2, max_digits=6, default=0)
 #    active = models.BooleanField(default=True)
 #    join_date = models.DateField(null=True)