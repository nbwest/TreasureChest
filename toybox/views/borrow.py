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

    # If borrow button has been pushed, handle borrow of toy and reload page

    # Only need to handle this frame is a toy is selected
    # TODO change this to POST - it performs the action of adding the toy
    # TODO somehow mark when a toy is to be borrowed (after toy add) vs just selecting it from the list

    # TODO newly borrowed toy criteria shouldn't be based on date - base on toy transaction - payment details.
    # OR added toys don't go into borrowed yet - List borrowed toys, store temporarily, add to this list, on accept commit to DB
    toy_code = request.GET.get('tc')
    if (toy_code):
        context.update(handle_toy_summary(request))
    # toy_code = request.GET.get('bt')
    # if (toy_code):
        toy = get_object_or_404(Toy, code=toy_code)
        member = get_object_or_404(Member, pk=member_id)
        print "Loaning toy"
        # TODO include borrow duration, 1 is placeholder, updated again when fee paid
        toy.borrow(member,1)

        # return HttpResponseRedirect(reverse('toybox:borrow', kwargs={'member_id': member_id}) )

    # TODO update member balance and transaction table
    # TODO update toy loan duration

    if (request.method == "POST"):
         payment_form = PaymentForm(request.POST)
         print("posted")
         if payment_form.is_valid():
            print("valid form")
            loan_duration = payment_form.cleaned_data['loan_duration']
            fee_due = payment_form.cleaned_data['fee_due']
            fee_paid = payment_form.cleaned_data['fee_paid']
            print(loan_duration)
            print(fee_due)
            print(fee_paid)
         else:
            print(payment_form.errors)
    else:
         payment_form=PaymentForm(initial={"loan_duration":2})


    context.update( handle_member_search(request))

    # Always need this so search box renders
    context.update(handle_toy_search(request))

    # Only need to handle these frames if member_id set
    if (member_id):
        context.update(handle_member_summary(request, member_id))
        context.update(handle_borrowed_toy_list(request, member_id))

    # TODO retrieve from elsewhere
    #base page context
    context.update({"daily_balance":23.20, "login_name":"Jess Benning"})

    context.update({"today": timezone.now()})

    context.update({'payment_form': payment_form})

    return render(request, 'toybox/borrow.html', context)


def handle_borrowed_toy_list(request, member_id):
    context = {}
    if (member_id):
        # toys = Toy.objects.all().annotate(due_in=F("due_date")-timezone.now()).filter(member_loaned=member_id)
        #toys= Toy.objects.all().extra(select={"difference":"due_date"-timezone.now()}).filter(member_loaned=member_id)
        toys = Toy.objects.filter(member_loaned=member_id).values()


#TODO time/date is wrong here - research timezone stuff
    if (toys):
        for t in toys:
            t.update({"due_in":(t["due_date"]-timezone.now().date()).days})

    context = {'toy_list': toys}

    return context


class HorizontalRadioRenderer(forms.RadioSelect.renderer):
  def render(self):
    return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


class PaymentForm(forms.Form):
    numeric = RegexValidator(r'^[0-9.]*$', 'Only numeric characters are allowed.')
    # TODO store these somewhere
    LOAN_CHOICES=[(1,"1"),(2,"2"),(6,"6")]

    loan_duration=forms.ChoiceField(choices=LOAN_CHOICES, widget=forms.RadioSelect(renderer=HorizontalRadioRenderer))
    fee_due = forms.CharField(label="Fee Due", max_length=20, validators=[numeric])
    fee_paid = forms.CharField(label="Fee Paid", max_length=20, validators=[numeric])