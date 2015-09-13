from django.shortcuts import render
from django.db.models import Count
from shared import *



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
    context.update(handle_member_search(request))

    if (request.method == "GET"):

        if (context["members"]!=None) or (member_id):
            context.update({"member_detail_submit_button_label":"Update"})
        else:
            context.update({"member_detail_submit_button_label":"Add"})

        if (member_id):
            context.update(handle_member_summary(request, member_id))
            form = MemberDetailsForm(initial=context["member"].__dict__,label_suffix="")
        else:
            form = MemberDetailsForm(label_suffix="")

        context.update({'member_details_form': form})

    #if no members have been searched for display all members
    if context["members"]==None:

        #get number of loans for each member
        overdue=Toy.objects.filter(due_date__lt=timezone.now().date())#.annotate(dcount=Count('member_loaned'))
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

        print(loans_overdue)
        print(loan_counts)

        context.update({"members":Member.objects.all().order_by('anniversary_date'),"loan_counts":loan_counts, "loans_overdue":loans_overdue})

    return context


def members(request, member_id=None):
    context=handle_member_details(request, member_id)
    return render(request, 'toybox/members.html', context)

def get_all_members_ordered_by_name():
    members=Member.objects.all().order_by('name')
    return members

#Form
class MemberDetailsForm(forms.Form):
    name=forms.CharField(label="Name", max_length=Member._meta.get_field('name').max_length)

    partner=forms.CharField(label="Partner Name", max_length=Member._meta.get_field('partner').max_length)
    phone_number1=forms.CharField(label="Primary Phone", max_length=Member._meta.get_field('phone_number1').max_length)
    phone_number2=forms.CharField(label="Secondary Phone", max_length=Member._meta.get_field('phone_number2').max_length)
    address=forms.CharField(label="Address", max_length=Member._meta.get_field('address').max_length)
    email_address=forms.CharField(label="Email", max_length=Member._meta.get_field('email_address').max_length)
    type=ModelChoiceField(queryset=MemberType.objects.all(),label="Member Type")
    balance = forms.CharField(label='Balance', widget=forms.TextInput(attrs={'readonly':'readonly'}))
    anniversary_date = forms.DateField(label='Membership due', widget=forms.TextInput(attrs={'readonly':'readonly'}))
    committee_member=forms.BooleanField(label="Committee Member")
    volunteer = forms.BooleanField(label="Volunteer")
    potential_volunteer = forms.BooleanField(label="Potential Volunteer")



 #children
 #    # anniversary_date = models.DateField('Membership due',null=True)
 #    active = models.BooleanField(default=True)
 #    join_date = models.DateField(null=True)