
from shared import *
from django.core.validators import *
from django.contrib.auth.decorators import login_required
import member_edit

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
    rendered = member_edit.render_ajax_request(request)
    if rendered != None:
        return rendered

    if request.method == "POST":
        member_edit.handle_member_edit(request, member_id)

    context = {"title":"Return Toy"}


    # if (request.method == "GET"):
    #      if "success" in request.GET:
    #          context.update({"success":True})


    context.update(base_data(request))
    context.update(handle_returns(request,member_id))


    if (member_id):
        context.update(handle_member_summary(request, member_id))
        context.update(handle_borrowed_toy_list(request, member_id))

    toyList=None
    if "toy_list" in context:
        toyList=context["toy_list"]


    return_date=thisDateTime().date()
    context.update({"return_date":return_date,"todays_date":return_date})

    if (request.method == "POST"):
        returns_form = ReturnsForm(request.POST,toyList=toyList)

        if returns_form.is_valid():

            past_return_date=returns_form.cleaned_data['return_date']
            todays_date=thisDateTime().date()

            if past_return_date != todays_date and 'Done' not in request.POST:
                return_date=past_return_date
                context.update({"return_date":past_return_date})
            else:
                for toy in toyList:
                    # print(returns_form.cleaned_data['issue_type_'+toy.code])
                    # print(returns_form.cleaned_data['issue_comment_'+toy.code])
                    # print(returns_form.cleaned_data['returned_checkbox_'+toy.code])

                    # toy.return_toy_with_issue()
                    # toy.issue_type=returns_form.cleaned_data['issue_type_'+toy.code]
                    # toy.issue_comment=returns_form.cleaned_data['issue_comment_'+toy.code]


                    if 'returned_checkbox_'+str(toy.id) in returns_form.cleaned_data:
                        if returns_form.cleaned_data['returned_checkbox_'+str(toy.id)]:
                            # return_date=returns_form.cleaned_data['return_date']
                            toy.return_toy(returns_form.cleaned_data['issue_type_'+str(toy.id)],returns_form.cleaned_data['issue_comment_'+str(toy.id)],request.user,return_date)

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

                    context.update({"success":True})




    loan_bond_enable= get_config("loan_bond_enable")


    context.update({"issue_list":Toy.ISSUE_TYPE_CHOICES,"loan_bond_enable":loan_bond_enable})#[:IssueChoiceType.RETURNED_MISSING_PIECE]})


    # display toy in toy summary
    # context.update(handle_toy_summary(request))

    context.update(handle_member_search(request))

    if toyList!=None:
        for toy in toyList:
            weeks_over=toy.weeks_overdue()
            days_over=(return_date-toy.due_date).days

            if days_over>6:

                toy.fine=weeks_over * toy.loan_cost

                if toy.fine > 0 and toy.fine > toy.purchase_cost and toy.purchase_cost > 0:
                    toy.fine=toy.purchase_cost

            else:
                toy.fine=0


    returns_form = ReturnsForm(toyList=toyList,initial={'return_date':return_date})

    context.update({"returns_form":returns_form})
    #print(context)

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

    return_date = forms.DateField(label="Return Date", input_formats=['%d/%m/%Y'], widget=forms.DateInput(format='%d/%m/%Y',attrs={'readonly':'readonly','title':'Date the toy(s) have been returned, defaults to today','button':'Refresh fees'}))


    loan_bond_enable= get_config("loan_bond_enable")

    numeric = RegexValidator(r'^[0-9.]*$', 'Only numeric characters are allowed.')

    late_fee = forms.CharField(required=False,label="Late Fee", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'enabled':'True','readonly':'readonly'}))
    issue_fee = forms.CharField( required=False,label="Issue Fee", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={ 'enabled':'True','readonly':'readonly'}))

    #works but needs a server restart
    if loan_bond_enable==True:
        loan_bond_refund = forms.CharField( required=False,label="Bond Refund", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={ 'enabled':'True','readonly':'readonly'}))


    total = forms.CharField(required=False,label="Total", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'hr':'True','enabled':'True','readonly':'readonly', 'button':'Done'}))




