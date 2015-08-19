from django.shortcuts import render
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

    context.update(handle_member_search(request))

    if (request.method == "GET"):

        if (context["members"]!=None) or (member_id):
            context.update({"member_detail_submit_button_label":"Update"})
        else:
            context.update({"member_detail_submit_button_label":"Add"})

        if (member_id):
            context.update(handle_member_summary(request, member_id))
            form = MemberDetailsForm(initial=context["member"],label_suffix="")
        else:
            form = MemberDetailsForm(label_suffix="")

    #if no members have been searched for display all members
    if context["members"]==None:
        context.update(get_all_members_names())

    context.update({'member_details_form': form})

    return context


def members(request, member_id=None):
    context=handle_member_details(request, member_id)
    return render(request, 'toybox/members.html', context)


#Form
class MemberDetailsForm(forms.Form):
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