from django.shortcuts import render
from django.db.models import Count
from shared import *
from django.utils import timezone
from django.contrib.auth.decorators import login_required


# POST - Guide: Use POST all the time except when you want the ability to bookmark a page, then use GET
#               Don't use GET to define actions
# GET
# /toybox/membership/ - display all members, clear form, submit button is "Add"
# /toybox/membership/1 - display all members, display member in form, submit button is "Update"
# /toybox/membership/?search=name_fragment - display search members, submit button is "Update"
# /toybox/membership/1/?search=name_fragment - display search members, submit button is "Update"



def handle_member_details(request, member_id):
    context = {"title":"Members"}
    form = None
    # context.update(handle_member_search(request))

    context.update({"members": get_all_members_ordered_by_name()})
    context.update({"member_toy_history":handle_member_toy_history(request,member_id)})

    if (request.method == "GET"):
        if (member_id):
            context.update({"member_detail_submit_button_label": "Update"})
            form = MemberDetailsForm(member_id=member_id, label_suffix="")
        else:
            context.update({"member_detail_submit_button_label": "Add"})
            form = MemberDetailsForm(label_suffix="")

        context.update({'member_details_form': form})

    # add or update member details
    if (request.method == "POST"):
        form = MemberDetailsForm(request.POST)

        if form.is_valid():
            form.save(member_id)
            context.update({"success":"true"})

        context.update({'member_details_form': form})


    # if no members have been searched for display all members
    if context["members"] != None:

        # get number of loans for each member
        overdue = Toy.objects.filter(
            due_date__lt=thisDateTime().date())  # .annotate(dcount=Count('member_loaned'))
        loans_overdue = {}
        for toy_due in overdue:
            if toy_due.member_loaned_id in loans_overdue:
                loans_overdue[toy_due.member_loaned_id] += 1
            else:
                loans_overdue.update({toy_due.member_loaned_id: 1})

        # probably a better way to do this, inserting into dict. better to have it attached to members in member list
        loans = Toy.objects.values('member_loaned').annotate(dcount=Count('member_loaned'))
        loan_counts = {}
        for loan in loans:
            if loan['dcount'] != 0:
                loan_counts.update({loan['member_loaned']: loan['dcount']})

        # print(loans_overdue)
        # print(loan_counts)

        context.update({"loan_counts": loan_counts, "loans_overdue": loans_overdue})
    # "members":Member.objects.all().order_by('membership_end_date'),
    return context


@login_required
def members(request, member_id=None):
    context = {}
    context.update(base_data(request))
    context.update(handle_member_details(request, member_id))
    return render(request, 'toybox/members.html', context)


def get_all_members_ordered_by_name():
    # members=Member.objects.all().order_by('name')
    members = Member.objects.filter(active=True).order_by('name')
    return members

def handle_member_toy_history(request, member_id):

    return ToyHistory.objects.filter(member__id=member_id).order_by('date_time').select_related('toy')


# Form
class MemberDetailsForm(forms.Form):
    credit_enable=get_config("credit_enable")

    name = forms.CharField(label="Name", max_length=Member._meta.get_field('name').max_length)

    partner = forms.CharField(required=False, label="Partner Name",
                              max_length=Member._meta.get_field('partner').max_length)
    # TODO all the number of max children to change
    child1 = forms.DateField(required=False, input_formats=['%d/%m/%Y'], label="Child 1 Birthday",widget=forms.DateInput(format='%d/%m/%Y',attrs={"datepicker": "True", 'group': 'Children'}))
    child2 = forms.DateField(required=False, input_formats=['%d/%m/%Y'], label="Child 2 Birthday",widget=forms.DateInput(format='%d/%m/%Y', attrs={"datepicker": "True"}))
    child3 = forms.DateField(required=False, input_formats=['%d/%m/%Y'], label="Child 3 Birthday",widget=forms.DateInput(format='%d/%m/%Y', attrs={"datepicker": "True"}))
    child4 = forms.DateField(required=False, input_formats=['%d/%m/%Y'], label="Child 4 Birthday",widget=forms.DateInput(format='%d/%m/%Y', attrs={"datepicker": "True"}))
    child5 = forms.DateField(required=False, input_formats=['%d/%m/%Y'], label="Child 5 Birthday",widget=forms.DateInput(format='%d/%m/%Y', attrs={"datepicker": "True"}))
    child6 = forms.DateField(required=False, input_formats=['%d/%m/%Y'], label="Child 6 Birthday",widget=forms.DateInput(format='%d/%m/%Y',attrs={"datepicker": "True", 'endgroup': 'Children'}))

    phone_number1 = forms.CharField(label="Primary Phone",max_length=Member._meta.get_field('phone_number1').max_length)
    phone_number2 = forms.CharField(required=False, label="Secondary Phone",max_length=Member._meta.get_field('phone_number2').max_length)
    address = forms.CharField(label="Address", max_length=Member._meta.get_field('address').max_length)
    email_address = forms.EmailField(label="Email", max_length=Member._meta.get_field('email_address').max_length)
    type = forms.ModelChoiceField(queryset=MemberType.objects.all(), label="Member Type")
    comment= forms.CharField(required=False, label="Comment", max_length=Member._meta.get_field('comment').max_length,widget=forms.Textarea())

    if credit_enable=="true":
        balance = forms.DecimalField(required=False, label='Balance',widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    join_date = forms.DateField(required=False, label='Join Date', input_formats=['%d/%m/%Y'],widget=forms.DateInput(format='%d/%m/%Y', attrs={'readonly': 'readonly'}))
    membership_end_date = forms.DateField(required=False, label='Membership due', input_formats=['%d/%m/%Y'],widget=forms.DateInput(format='%d/%m/%Y', attrs={'readonly': 'readonly'}))
    bond_fee_paid = forms.DecimalField(required=False, label='Bond',widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    committee_member = forms.BooleanField(required=False, label="Committee Member")
    volunteer = forms.BooleanField(required=False, label="Active Volunteer")
    potential_volunteer = forms.BooleanField(required=False, label="Potential Volunteer")
    volunteer_capacity_wed = forms.BooleanField(required=False, label="Wednesday Volunteer Capacity")
    volunteer_capacity_sat = forms.BooleanField(required=False, label="Saturday Volunteer Capacity")

    def save(self,member_id):
        self.cleaned_data.pop("membership_end_date")
        if "balance" in self.cleaned_data:
            self.cleaned_data.pop("balance")
        self.cleaned_data.pop("join_date")
        self.cleaned_data.pop("bond_fee_paid")
        #
        # type=self.cleaned_data.pop("type")
        #
        # self.cleaned_data.update({"type":type.pk})



        children = {}
        for key in self.cleaned_data.keys():
            if key.startswith('child'):
                if self.cleaned_data[key]:
                    children.update({key: self.cleaned_data[key]})
                self.cleaned_data.pop(key)


        print self.cleaned_data["type"]

        result=Member.objects.update_or_create(pk=member_id, defaults=self.cleaned_data)

        #delete existing children for updated member
        if not result[1]:
            Child.objects.filter(parent=member_id).delete()

        member=result[0]

        for dob in children.values():
            Child.objects.create(parent=member, date_of_birth=dob)




    def form_initial(self,member_id):
        children = Child.objects.filter(parent=member_id)
        initial = get_object_or_404(Member, pk=member_id).__dict__

        #foreign key type is given name type_id, this doesn't set the type correctly, must be called type - copy it
        initial.update({"type":initial["type_id"]})
        initial.pop("type_id")
        counter = 1
        for child in children:
            initial.update({"child" + str(counter): child.date_of_birth})
            counter += 1
        return initial

    def __init__(self, *args, **kwargs):
        member_id=kwargs.pop("member_id", 0)
        if member_id:
            kwargs.update({"initial":self.form_initial(member_id)})
        super(MemberDetailsForm, self).__init__(*args, **kwargs)



