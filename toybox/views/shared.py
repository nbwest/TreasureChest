from django import forms
from django.shortcuts import get_object_or_404
from toybox.models import *
from django.db.models import Q



#################
# general helpers
def fragment_search(fragment):
    if fragment != '':
        return Member.objects.filter(Q(name__contains=fragment)|Q(partner__contains=fragment)).order_by("name")
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
    error=""

    # Search pressed.  Validate form and get list of matching members
    if (request.method == "GET"):
        form = MemberSearchForm(request.GET)
        if form.is_valid():
            name_fragment=form.cleaned_data['member_name_fragment'].strip()
            if name_fragment!="":
                possible_members = fragment_search(name_fragment)

                if possible_members.__len__()==0:
                    error="No members found"
            #else:
                #error="Member name not entered"
            if error!="":
                form.add_error("member_name_fragment",error)
    else:
         form = MemberSearchForm()

    context = {'member_search_form': form,
               'members': possible_members}

    return context


def handle_member_summary(request, member_id):
    context = {}
    if (member_id):
        credit_enable=get_config("credit_enable")
        member = get_object_or_404(Member, pk=member_id)
        children = Child.objects.filter(parent=member_id)
        context = {'member': member,'children': children,'credit_enable':credit_enable}
        #print(context["member"])
    return context



def handle_borrowed_toy_list(request, member_id):
    context = {}
    if (member_id):
        toys=Toy.objects.filter(member_loaned=member_id)

    context = {'toy_list': toys}

    return context



def get_members(*fields,**kwargs):
    return {"members":Member.objects.filter(kwargs).values(fields)}



def base_data(request):
    version="V1.1.1"
    context={}

    context.update({"daily_balance": Transaction.objects.latest().balance,"version":version})
    return context

##################
# Shared form classes
class MemberSearchForm(forms.Form):
    member_name_fragment = forms.CharField(label="Member Name", max_length=20,required=False)

class ToySearchForm(forms.Form):
    toy_search_string = forms.CharField(label="ID or name of toy to borrow", max_length=10,required=False)


def get_config(key):
    try:

        return(Config.objects.get(key=key).value.lower())

    except Config.DoesNotExist:

        if key=="credit_enable":
            return("true")

        elif key=="repair_loan_duration":
            return("26")

        elif key=="loan_bond_enable":
            return('true')

        elif key=="default_loan_duration":
            return("2")

        elif key=="max_toys":
            return(4)

        elif key=="loan_durations":
            return("12")

        elif key=="donation_enable":
            return("true")

        else:
            raise NameError('Option key not found: '+key)

