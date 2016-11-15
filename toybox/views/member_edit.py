
from toybox.models import *
from django import forms
from django.shortcuts import get_object_or_404
from shared import get_config
from django.template.loader import render_to_string
from django.shortcuts import HttpResponse

def handle_member_edit(request, member_id):
    context = {"title":"Members"}
    form = None
    # context.update(handle_member_search(request))

    # context.update({"members": get_all_members_ordered_by_name()})
    # context.update({"member_toy_history":handle_member_toy_history(request,member_id)})

    if (request.method == "GET"):
        if (member_id):
            context.update({"member_detail_submit_button_label": "Update"})
            form = MemberDetailsForm(member_id=member_id, label_suffix="")
        else:
            context.update({"member_detail_submit_button_label": "Add"})
            form = MemberDetailsForm(label_suffix="")

        context.update({'member_edit_form': form})

    # add or update member details
    if (request.method == "POST"):
        form = MemberDetailsForm(request.POST)

        if form.is_valid():
            form.save(member_id)
            context.update({"success":"true"})
        else:
            context.update({"failure":"true"})

        context.update({'member_edit_form': form})



    # "members":Member.objects.all().order_by('membership_end_date'),
    return context



class MemberDetailsForm(forms.Form):
    credit_enable=get_config("credit_enable")

    name = forms.CharField(label="Name", max_length=Member._meta.get_field('name').max_length)

    partner = forms.CharField(required=False, label="Alternate Borrower Name",
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



    committee_member = forms.BooleanField(required=False, label="Committee Member")
    volunteer = forms.BooleanField(required=False, label="Active Volunteer")
    potential_volunteer = forms.BooleanField(required=False, label="Potential Volunteer")
    volunteer_capacity_wed = forms.BooleanField(required=False, label="Wednesday Volunteer Capacity")
    volunteer_capacity_sat = forms.BooleanField(required=False, label="Saturday Volunteer Capacity")

    if credit_enable=="true":
        balance = forms.DecimalField(required=False, label='Balance',widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    comment= forms.CharField(required=False, label="Comment", max_length=Member._meta.get_field('comment').max_length,widget=forms.Textarea())

    join_date = forms.DateField(required=False, label='Join Date', input_formats=['%d/%m/%Y'],widget=forms.DateInput(format='%d/%m/%Y', attrs={'readonly': 'readonly'}))
    membership_end_date = forms.DateField(required=False, label='Membership due', input_formats=['%d/%m/%Y'],widget=forms.DateInput(format='%d/%m/%Y', attrs={'readonly': 'readonly'}))
    bond_fee_paid = forms.DecimalField(required=False, label='Bond',widget=forms.TextInput(attrs={'readonly': 'readonly'}))
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

def render_member_edit(request):

    rendered=None
    context={}

    if request.method=="GET":
         if "member_edit_id" in request.GET:
            member_id=request.GET["member_edit_id"]
            context.update(handle_member_edit(request,member_id))
            rendered=render_to_string('toybox/member_edit.html', context)

    return rendered


def render_ajax_request(request):

    if request.method=="GET" and request.is_ajax():
         if "member_edit_id" in request.GET:
             rendered=render_member_edit(request)

         return HttpResponse(rendered)

    return None