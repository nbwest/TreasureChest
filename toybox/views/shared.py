
from django import forms
from django.shortcuts import get_object_or_404
from toybox.models import *
from django.db.models import Q
from django.conf import settings



#################
# general helpers
def fragment_search(fragment):
    if fragment != '':
        return Member.objects.filter(Q(name__icontains=fragment)|Q(partner__icontains=fragment)).exclude(active=False).order_by("name")
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

def thisDateTime():
    return timezone.make_aware(datetime.datetime.now(),timezone.get_default_timezone())

def get_members(*fields,**kwargs):
    return {"members":Member.objects.filter(kwargs).values(fields)}

def updateDailyBalance():
    latest_balance=0
    if Transaction.objects.count() >0:
        latest_balance=Transaction.objects.latest().balance
    return {"daily_balance":latest_balance}

def base_data(request):


    context={"version":settings.VERSION}


    context.update(updateDailyBalance())


    if 'first_login' not in request.session:
        request.session.update({'first_login':True})
    else:
        context.update({"enable_logout_button":"true"})

    #set till popup for login and kogoff
    if (request.method == "POST"):
        if "till_value" in request.POST:

            if "till_set" in request.POST:
                from toybox.views.transactions import setTill
                try:
                    setTill(request.POST['till_value'],context['daily_balance'],request)
                except ValueError as e:
                    context.update({"till_value_error":e.message})
                    return context
                else:
                    context.update(updateDailyBalance())


            #for tilll set on login
            if 'first_login' in request.session:
                if request.session['first_login']==True:
                    request.session.update({'first_login':False})
                else:
                     request.session.update({'logout':True})#issue here for transaction page, needs this to set till on logout

    return context

##################
# Shared form classes
class MemberSearchForm(forms.Form):
    member_name_fragment = forms.CharField(label="Member Name", max_length=20,required=False,widget=forms.TextInput(attrs={'title': 'Enter member name fragment'}))

class ToySearchForm(forms.Form):
    toy_search_string = forms.CharField(label="Exact ID or name fragment of toy to borrow", max_length=100,required=False,widget=forms.TextInput(attrs={'title': 'Enter toy ID or toy name fragment'}))


def get_config(key):

    try:
        value=Config.objects.get(key=key).value.lower()
        value_type=Config.objects.get(key=key).value_type

        # return value

        if value_type == Config.NUMBER:
            try:
                return Decimal(value)
            except:
                raise NameError("Value: "+value+" is not type: "+Config.CONFIG_TYPES[value_type][1])
                return None

        elif value_type == Config.BOOLEAN:
            if value in set(["0","no","n","false"]):
                return False
            elif value in set(["1","yes","y","true"]):
                return True
            else:
                raise NameError("Value: "+value+" is not type: "+Config.CONFIG_TYPES[value_type][1])
                return None

        elif value_type == Config.STRING:
            return value

        else:
            raise NameError("Invalid type")


    except Config.DoesNotExist:

        if key=="credit_enable":
            return(True)

        elif key=="repair_loan_duration":
            return(26)

        elif key=="loan_bond_enable":
            return(True)

        elif key=="default_loan_duration":
            return(2)

        elif key=="max_toys":
            return(4)

        elif key=="loan_durations":
            return(12)

        elif key=="donation_enable":
            return(True)

        elif key=="major_issue_multiplier_min":
            return(0.1)

        elif key=="minor_issue_multiplier_min":
            return(0.0)

        elif key=="major_issue_multiplier_max":
            return(0.5)

        elif key=="minor_issue_multiplier_max":
            return(0.0)

        else:
            raise NameError('Option key not found: '+key)
            return None

