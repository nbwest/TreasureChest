from django.shortcuts import render
from shared import *
from django import forms
from django.core.validators import *

def transactions(request):

    context={}

    # form=TransactionForm(request.POST)
    # context={"transaction_form":form}
    context.update({"transactions":Transaction.objects.all().order_by('date_time')})

    # print(Transaction.TRANSACTION_EXTRA[Transaction.MEMBER_DEPOSIT_REFUND][Transaction.TRANSACTION_DIRECTION])
    # print(Transaction.TRANSACTION_EXTRA[Transaction.MEMBER_DONATION][Transaction.ACCESS_TYPE])

    return render(request, 'toybox/transactions.html',context )


# class TransactionForm(forms.Form):
#     date_from = forms.DateField(required=False)
#     date_to = forms.DateField(required=False)
#     member = forms.ModelChoiceField(required=False,queryset=Member.objects.all())
#
#     TRANSACTION_TYPE_CHOICES =  list(Transaction.TRANSACTION_TYPE_CHOICES)
#     TRANSACTION_TYPE_CHOICES.insert(0,(-1,'---------'))
#
#
#     filter_type=forms.ChoiceField(required=False,choices=TRANSACTION_TYPE_CHOICES,  initial=-1)
