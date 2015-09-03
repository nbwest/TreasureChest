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
    error=""

    # Search pressed.  Validate form and get list of matching members
    if (request.method == "GET"):
        form = MemberSearchForm(request.GET)
        if form.is_valid():
            name_fragment=form.cleaned_data['member_name_fragment']
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
        member = get_object_or_404(Member, pk=member_id)
        children = Child.objects.filter(parent=member_id)
        context = {'member': member,'children': children}
        #print(context["member"])
    return context

#also adds toy to temp list in DB via POST - not sure if this is a good idea
def handle_toy_search(request,member_id):

    toys = None
    error=""
    toycode=""

    form = ToySearchForm(request.POST)

    if (request.method == "POST"):
        if form.is_valid():
            toycode=form.cleaned_data['toy_id']

            if toycode=="":
                error="Toy code not entered"
            else:
                toy = Toy.objects.filter(code=toycode, state=Toy.AT_TOY_LIBRARY)

                if toy.count()>0:
                    in_temp_list=TempBorrowList.objects.filter(toy=toy[0])

                    if not in_temp_list:
                        member = get_object_or_404(Member, pk=member_id)
                        tempBorrowList=TempBorrowList()
                        tempBorrowList.store(member,toy[0])
                    else:
                        error="Toy on loan"
                else:
                    error="Toy not found"
                    if (member_id):
                        if (Toy.objects.filter(member_loaned=member_id, code=toycode).count()>0):
                            error="Toy on loan"

            if error!="":
                form.add_error("toy_id",error)

    elif request.method == "GET":
        toycode = request.GET.get('tc')

    if form.is_valid() and toycode:
        toys = get_list_or_404(Toy,code__contains=toycode)

    context = {'toy_search_form': form, 'toys': toys}
    
    return context


def handle_toy_summary(request):
    context={}

    if request.method == "GET":
        toycode = request.GET.get('tc')

    if request.method == "POST":
        form=ToySearchForm(request.POST)
        if form.is_valid():
            toycode=form.cleaned_data['toy_id']

    if (toycode):
        toy = get_object_or_404(Toy, code=toycode)
        context = {'toy': toy, "loan_type__loan_cost":toy.loan_type.loan_cost}

    return context


def handle_borrowed_toy_list(request, member_id):
    context = {}
    if (member_id):
        toys=Toy.objects.filter(member_loaned=member_id)

    context = {'toy_list': toys}

    return context



def get_members(*fields,**kwargs):
    return {"members":Member.objects.filter(kwargs).values(fields)}


def get_all_members_names():
     return {"members":Member.objects.values("name","id")}



##################
# Shared form classes
class MemberSearchForm(forms.Form):
    member_name_fragment = forms.CharField(label="Member Name", max_length=20,required=False)

class ToySearchForm(forms.Form):
    toy_id = forms.CharField(label="Toy ID", max_length=10,required=False)

