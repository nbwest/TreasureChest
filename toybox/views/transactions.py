from django.shortcuts import render
from shared import *
from django import forms
from django.core.validators import *

def transactions(request):

    context={}

    form=TransactionForm(request.POST)
    context={"transaction_form":form}
    context.update({"transactions":Transaction.objects.all().order_by('date_time')})


    return render(request, 'toybox/transactions.html',context )


class TransactionForm(forms.Form):
    date_from = forms.DateField(required=False)
    date_to = forms.DateField(required=False)
    member = forms.ModelChoiceField(required=False,queryset=Member.objects.all())
    toy=forms.ModelChoiceField(required=False,queryset=Toy.objects.all())
    filter_type=forms.ChoiceField(required=False,choices=Transaction.TRANSACTION_TYPE_CHOICES,  initial=Transaction.DEBIT_ADJUSTMENT)
