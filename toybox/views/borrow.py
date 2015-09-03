from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from shared import *
from django.db.models import *
from django.core.validators import *
from django.utils.safestring import mark_safe
from datetime import *

# TODO limit toys to four - have this number stored somewhere



# work flow
# member is searched for and once selected displays user stats
# existing borrowed toys appear in toy list - these can't be removed and there are no fees
# User enters a toy to be borrowed
# toy appears in borrowed displayed toys list
# user selects borrow duration - toy fee in list adjusts
# on fee being collected, done commits new toys to DB



def borrow(request, member_id):
    context={}


    #TODO retrieve from elsewhere
    #base page context
    context.update({"daily_balance":23.20, "login_name":"Jess Benning"})

    #display toy in toy summary
    context.update(handle_toy_summary(request))

    #handle member search
    context.update( handle_member_search(request))

    # if member_id set display member summary and list of borrowed toys
    if (member_id):
        context.update(handle_member_summary(request, member_id))
        context.update(handle_borrowed_toy_list(request, member_id))

    # Always need this so search box renders
    context.update(handle_toy_search(request,member_id))

    new_borrow_list=TempBorrowList.objects.filter(member=member_id)
    context.update({"new_borrow_list":new_borrow_list})

    if request.method=="POST":
        for item in request.POST:
            if item.startswith("remove_toy_"):
                toy_to_remove=item[len("remove_toy_"):]
                TempBorrowList.objects.filter(toy__code=toy_to_remove, member__id=member_id).delete()
                print(toy_to_remove)




    context.update(handle_payment_form(request))

    return render(request, 'toybox/borrow.html', context)



def handle_payment_form(request):
     # TODO update member balance and transaction table
    # TODO update toy loan duration
    context={}
    if (request.method == "POST"):
         payment_form = PaymentForm(request.POST)
         #print("posted")
         if payment_form.is_valid():
            #print("valid form")
            loan_duration = payment_form.cleaned_data['loan_duration']
            fee_due = payment_form.cleaned_data['fee_due']
            fee_paid = payment_form.cleaned_data['fee_paid']

            #print(loan_duration)
            #print(fee_due)
            #print(fee_paid)
        # else:
            #print(payment_form.errors)
    else:
        # TODO store default duration in settings
         payment_form=PaymentForm(initial={"loan_duration":"2"})

    context={'payment_form': payment_form}

    return context

class HorizontalRadioRenderer(forms.RadioSelect.renderer):
  def render(self):
    return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


class PaymentForm(forms.Form):
    numeric = RegexValidator(r'^[0-9.]*$', 'Only numeric characters are allowed.')
    # TODO store loan durations in settings
    LOAN_DURATIONS="126"
    LOAN_CHOICES=[]

    #so choices can be easily stored in settings
    for c in LOAN_DURATIONS:
        LOAN_CHOICES.append((c,c))


    loan_duration=forms.ChoiceField(choices=LOAN_CHOICES, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer))
    fee_due = forms.CharField(label="Fee Due", max_length=20, validators=[numeric])
    fee_paid = forms.CharField(label="Fee Paid", max_length=20, validators=[numeric])