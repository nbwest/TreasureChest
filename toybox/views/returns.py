from django.shortcuts import render
from shared import *
from django.core.validators import *
from django.forms.formsets import formset_factory
from django.contrib.auth.decorators import login_required

@login_required
def handle_returns(request,member_id):
    context={}

    context.update(handle_member_search(request))

    if (request.method == "GET"):
        if (member_id):
            context.update(handle_member_summary(request, member_id))

    return context


@login_required
def returns(request, member_id=None):

    context={}
    context.update(base_data(request))
    context.update(handle_returns(request,member_id))


    if (member_id):
        context.update(handle_member_summary(request, member_id))
        context.update(handle_borrowed_toy_list(request, member_id))

    toyList=None
    if "toy_list" in context:
        toyList=context["toy_list"]




    if (request.method == "POST"):
        returns_form = ReturnsForm(request.POST,toyList=toyList)

        if returns_form.is_valid():

            for toy in toyList:
                # print(returns_form.cleaned_data['issue_type_'+toy.code])
                # print(returns_form.cleaned_data['issue_comment_'+toy.code])
                # print(returns_form.cleaned_data['returned_checkbox_'+toy.code])

                # toy.return_toy_with_issue()
                # toy.issue_type=returns_form.cleaned_data['issue_type_'+toy.code]
                # toy.issue_comment=returns_form.cleaned_data['issue_comment_'+toy.code]


                if 'returned_checkbox_'+str(toy.id) in returns_form.cleaned_data:
                    if returns_form.cleaned_data['returned_checkbox_'+str(toy.id)]:
                        toy.return_toy(returns_form.cleaned_data['issue_type_'+str(toy.id)],returns_form.cleaned_data['issue_comment_'+str(toy.id)],request.user)
                    # toy.return_toy()



            if (member_id):

                member = get_object_or_404(Member, pk=member_id)

                if 'issue_fee' in returns_form.cleaned_data:
                    if returns_form.cleaned_data['issue_fee']!="":
                        fee=float(returns_form.cleaned_data['issue_fee'])
                        if fee!=0:
                            transaction=Transaction()
                            transaction.create_transaction_record(request.user,member,Transaction.ISSUE_FEE,fee,None,False)

                if 'late_fee' in returns_form.cleaned_data:
                    if returns_form.cleaned_data['late_fee']!="":
                        fee=float(returns_form.cleaned_data['late_fee'])
                        if fee!=0:
                            transaction=Transaction()
                            transaction.create_transaction_record(request.user, member,Transaction.LATE_FEE,fee,None,False)

                if 'loan_bond_refund' in returns_form.cleaned_data:
                    if returns_form.cleaned_data['loan_bond_refund']!="":
                        fee=float(returns_form.cleaned_data['loan_bond_refund'])
                        if fee!=0:
                            transaction=Transaction()
                            transaction.create_transaction_record(request.user, member,Transaction.LOAN_BOND_REFUND,fee,None,False)


                context.pop("toy_list",None)
                context.pop("member",None)



    try:
        loan_bond_enable= Config.objects.get(key="loan_bond_enable").value.lower
    except Config.DoesNotExist:
        loan_bond_enable= 'true'

    context.update({"issue_list":Toy.ISSUE_TYPE_CHOICES,"loan_bond_enable":loan_bond_enable})#[:IssueChoiceType.RETURNED_MISSING_PIECE]})


    # display toy in toy summary
    # context.update(handle_toy_summary(request))

    context.update(handle_member_search(request))

    if toyList!=None:
        for toy in toyList:
            if toy.weeks_overdue()>0:
                toy.fine=toy.weeks_overdue()* toy.loan_cost
            else:
                toy.fine=0


    returns_form = ReturnsForm(toyList=toyList)

    context.update({"returns_form":returns_form})
    print(context)

    return render(request, 'toybox/returns.html', context)



class ReturnsForm(forms.Form):



    def __init__(self, *args, **kwargs):
        toyList=kwargs.pop("toyList", 0)
        super(ReturnsForm, self).__init__(*args, **kwargs)

        if toyList:
            for toy in toyList:
                self.fields['returned_checkbox_%s' % toy.id]=forms.BooleanField(required=False)
                self.fields['issue_comment_%s' % toy.id] = forms.CharField(required=False,initial=toy.issue_comment, max_length=ToyHistory._meta.get_field('issue_comment').max_length)
                self.fields['issue_type_%s' % toy.id] = forms.ChoiceField(required=False,initial=toy.issue_type, choices=Toy.ISSUE_TYPE_CHOICES[:Toy.RETIRE_VERIFIED])

    try:
        loan_bond_enable= Config.objects.get(key="loan_bond_enable").value.lower
    except Config.DoesNotExist:
        loan_bond_enable= 'true'

    numeric = RegexValidator(r'^[0-9.]*$', 'Only numeric characters are allowed.')

    late_fee = forms.CharField(required=False,label="Late Fee", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'enabled':'True','readonly':'readonly'}))
    issue_fee = forms.CharField( required=False,label="Issue Fee", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={ 'enabled':'True','readonly':'readonly'}))

    #works but needs a server restart
    if loan_bond_enable=="true":
        loan_bond_refund = forms.CharField( required=False,label="Bond Refund", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={ 'enabled':'True','readonly':'readonly'}))


    total = forms.CharField(required=False,label="Total", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'hr':'True','enabled':'True','readonly':'readonly', 'done_button':'True'}))




