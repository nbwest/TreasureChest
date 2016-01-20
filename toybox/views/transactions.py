from django.shortcuts import render
from shared import *
from django import forms
from django.core.validators import *
import decimal

def transactions(request):
    till_value_error=""
    bank_value_error=""
    context={}
    form=None
    context.update(base_data())


    if (request.method == "POST"):
        form=TransactionForm(request.POST)
        if form.is_valid():
            # new_till_value=form.cleaned_data['till_value']

            if "button_set_till" in request.POST:
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
                                till_value_error="Value must be different to balance"
                        else:
                            till_value_error="Negative numbers not accepted"


            if "button_bank_amount" in request.POST:
                if "bank_value" in form.cleaned_data:
                    if form.cleaned_data['bank_value']!="":
                        value=decimal.Decimal(form.cleaned_data['bank_value'])
                        current_till=context['daily_balance']
                        if value>=0:
                            if current_till-value>0:
                                    #TODO set volunteer
                                 transaction=Transaction()
                                 type=Transaction.ADJUSTMENT_CREDIT
                                 transaction.create_transaction_record(None,type,-value,comment="BANK TILL",balance_change=-value)
                            else:
                                bank_value_error="Invalid amount - Till less than zero"
                        else:
                            bank_value_error="Negative numbers not accepted"

            if "button_bank_all" in request.POST:
                transaction=Transaction()
                transaction.create_transaction_record(None,Transaction.ADJUSTMENT_DEBIT,-context['daily_balance'],comment="BANK ALL TILL",balance_change=-context['daily_balance'])

            #call to update current balance after transactions
            context.update(base_data())


    if form:
        if bank_value_error!="" or len(form.errors)>0:
            form.add_error("bank_value", bank_value_error)

        if till_value_error!="" or len(form.errors)>0:
            form.add_error("till_value", till_value_error)
    else:
        form=TransactionForm(daily_balance=context['daily_balance'])


    context.update({"transaction_form":form})
    context.update({"transactions":Transaction.objects.all().order_by('date_time')})


    return render(request, 'toybox/transactions.html',context )


class TransactionForm(forms.Form):

    balance=0.0

    def __init__(self, *args, **kwargs):
            self.balance=kwargs.pop("daily_balance", 0)
            super(TransactionForm, self).__init__(*args, **kwargs)
            numeric = RegexValidator(r'^[0-9.-]*$', 'Only numeric characters are allowed.')
            self.fields['bank_value']= forms.CharField(required=False, label="Remove from Till $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'button_bank_amount':'Bank Amount','button_bank_all':'Bank '+'${:,.2f}'.format(self.balance) }))
            self.fields['till_value']= forms.CharField(required=False, label="New Till value $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={ 'button_set_till':'Set Till'}))

    till_value = forms.CharField()
    bank_value = forms.CharField()

