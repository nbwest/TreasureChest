from django.shortcuts import render
from django.db.models import Count
from shared import *
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# POST - Guide: Use POST all the time except when you want the ability to bookmark a page, then use GET
#               Don't use GET to define actions
# GET
#/toybox/membership/ - display all members, clear form, submit button is "Add"
#/toybox/membership/1 - display all members, display member in form, submit button is "Update"
#/toybox/membership/?search=name_fragment - display search members, submit button is "Update"
#/toybox/membership/1/?search=name_fragment - display search members, submit button is "Update"


def handle_member_details(request, member_id):
    context={}
    form=None
    #context.update(handle_member_search(request))

    context.update({"members":get_all_members_ordered_by_name()})



    if (request.method == "GET"):
# (context["members"] != None) or

        if member_id != None:
            context.update({"member_detail_submit_button_label":"Update"})
        else:
            context.update({"member_detail_submit_button_label":"Add"})

        if (member_id):
            context.update(handle_member_summary(request, member_id))
            form = MemberDetailsForm(initial=context["member"].__dict__,label_suffix="")
        else:
            form = MemberDetailsForm(label_suffix="")

        context.update({'member_details_form': form})

    #add or update member details
    if (request.method == "POST"):
        form = MemberDetailsForm(request.POST)
        if form.is_valid():
            if "add" in request.POST:
                form.cleaned_data.pop("membership_end_date")
                form.cleaned_data.pop("balance")
                Member.objects.create(**form.cleaned_data)
            elif "update" in request.POST:
               Member.objects.filter(pk=member_id).update(**form.cleaned_data)

        context.update({'member_details_form': form})

    #if no members have been searched for display all members
    if context["members"] != None:

        #get number of loans for each member
        overdue=Toy.objects.filter(due_date__lt=datetime.datetime.now().date())#.annotate(dcount=Count('member_loaned'))
        loans_overdue={}
        for toy_due in overdue:
            if toy_due.member_loaned_id in loans_overdue:
                loans_overdue[toy_due.member_loaned_id] += 1
            else:
                loans_overdue.update({toy_due.member_loaned_id:1})

        #probably a better way to do this, inserting into dict. better to have it attached to members in member list
        loans=Toy.objects.values('member_loaned').annotate(dcount=Count('member_loaned'))
        loan_counts={}
        for loan in loans:
            if loan['dcount']!=0:
                loan_counts.update({loan['member_loaned']:loan['dcount']})

        # print(loans_overdue)
        # print(loan_counts)

        context.update({"loan_counts":loan_counts, "loans_overdue":loans_overdue})
# "members":Member.objects.all().order_by('membership_end_date'),
    return context

@login_required
def members(request, member_id=None):
    context={}
    context.update(base_data(request))
    context.update(handle_member_details(request, member_id))
    return render(request, 'toybox/members.html', context)

def get_all_members_ordered_by_name():
    # members=Member.objects.all().order_by('name')
    members=Member.objects.filter(active=True).order_by('name')
    return members

#Form
class MemberDetailsForm(forms.Form):
    name=forms.CharField(label="Name", max_length=Member._meta.get_field('name').max_length)

    partner=forms.CharField(required=False,label="Partner Name", max_length=Member._meta.get_field('partner').max_length)
    phone_number1=forms.CharField(label="Primary Phone", max_length=Member._meta.get_field('phone_number1').max_length)
    phone_number2=forms.CharField(required=False,label="Secondary Phone", max_length=Member._meta.get_field('phone_number2').max_length)
    address=forms.CharField(label="Address", max_length=Member._meta.get_field('address').max_length)
    email_address=forms.CharField(label="Email", max_length=Member._meta.get_field('email_address').max_length)
    type=forms.ModelChoiceField(queryset=MemberType.objects.all(),label="Member Type")
    balance = forms.DecimalField(required=False,label='Balance', widget=forms.TextInput(attrs={'readonly':'readonly'}))
    membership_end_date = forms.DateField(required=False,label='Membership due', widget=forms.TextInput(attrs={'readonly':'readonly'}))
    deposit_fee_paid = forms.DecimalField(required=False,label='Deposit', widget=forms.TextInput(attrs={'readonly':'readonly'}))
    committee_member=forms.BooleanField(required=False,label="Committee Member")
    volunteer = forms.BooleanField(required=False,label="Active Volunteer")
    potential_volunteer = forms.BooleanField(required=False,label="Potential Volunteer")
    volunteer_capacity_wed = forms.BooleanField(required=False,label="Wednesday Volunteer Capacity")
    volunteer_capacity_sat = forms.BooleanField(required=False,label="Saturday Volunteer Capacity")




 #children
 #    # anniversary_date = models.DateField('Membership due',null=True)
 #    active = models.BooleanField(default=True)
 #    join_date = models.DateField(null=True)
