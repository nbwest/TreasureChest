from django.shortcuts import render
from shared import *
from django import forms
from django.core.validators import *
from django.forms.util import ErrorList
import decimal

def transactions(request):
    error=""
    context={}
    context.update(base_data())


    if (request.method == "POST"):
        form=TransactionForm(request.POST)
        if form.is_valid():
            new_till_value=form.cleaned_data['till_value']

            if "Set Till" in request.POST:
                if "till_value" in form.cleaned_data:
                    if form.cleaned_data['till_value']!="":
                        value=decimal.Decimal(form.cleaned_data['till_value'])
                        current_till=context['daily_balance']
                        if value>=0:
                            if current_till!=value:
                                #TODO set volunteer

                                 transaction=Transaction()

                                 if value>current_till:
                                     type=Transaction.ADJUSTMENT_CREDIT
                                     adj=value-current_till
                                 else:
                                     type=Transaction.ADJUSTMENT_DEBIT
                                     adj=-(current_till-value)

                                 transaction.create_transaction_record(None,type,adj,comment="TILL ADJ",balance_change=adj)
                            else:
                                error="Value must be different to balance"
                        else:
                            error="Negative numbers not accepted"
            if "Bank Till" in request.POST:
                transaction=Transaction()
                transaction.create_transaction_record(None,Transaction.ADJUSTMENT_DEBIT,-context['daily_balance'],comment="BANK TILL",balance_change=-context['daily_balance'])

            #call to update current balance after transactions
            context.update(base_data())



    if error!="" or len(form.errors)>0:
        form.add_error("till_value", error)
    else:
        form=TransactionForm(initial={'bank_value':context['daily_balance']})


    context.update({"transaction_form":form})
    context.update({"transactions":Transaction.objects.all().order_by('date_time')})

    # print(Transaction.TRANSACTION_EXTRA[Transaction.MEMBER_DEPOSIT_REFUND][Transaction.TRANSACTION_DIRECTION])
    # print(Transaction.TRANSACTION_EXTRA[Transaction.MEMBER_DONATION][Transaction.ACCESS_TYPE])

    return render(request, 'toybox/transactions.html',context )


class TransactionForm(forms.Form):

    numeric = RegexValidator(r'^[0-9.-]*$', 'Only numeric characters are allowed.')

    till_value = forms.CharField(required=False, label="New Till value $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={ 'add_button':'Set Till'}))
    bank_value = forms.CharField(required=False, label="Current Till $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'readonly':'readonly', 'add_button':'Bank Till'}))


#     date_from = forms.DateField(required=False)
#     date_to = forms.DateField(required=False)
#     member = forms.ModelChoiceField(required=False,queryset=Member.objects.all())
#
#     TRANSACTION_TYPE_CHOICES =  list(Transaction.TRANSACTION_TYPE_CHOICES)
#     TRANSACTION_TYPE_CHOICES.insert(0,(-1,'---------'))
#
#
#     filter_type=forms.ChoiceField(required=False,choices=TRANSACTION_TYPE_CHOICES,  initial=-1)
