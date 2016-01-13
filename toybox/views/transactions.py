from django.shortcuts import render
from shared import *
from django import forms
from django.core.validators import *
from django.contrib.auth.decorators import login_required

@login_required()
def transactions(request):
    form=TransactionForm(request.POST)
    context={"transaction_form":form}
    return render(request, 'toybox/transactions.html',context )


class TransactionForm(forms.Form):
    date_from = forms.DateField()
    date_to = forms.DateField()
    filter_type=forms.ChoiceField(choices=Transaction.TRANSACTION_TYPE_CHOICES,  initial=Transaction.DEBIT_ADJUSTMENT)
