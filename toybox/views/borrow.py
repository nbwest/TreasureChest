from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from shared import *
from django.db.models import *
from django.core.validators import *
from django.utils.safestring import mark_safe
from datetime import *
import decimal

# TODO limit toys to four - have this number stored somewhere



# work flow
# member is searched for and once selected displays user stats
# existing borrowed toys appear in toy list - these can't be removed and there are no fees
# User enters a toy to be borrowed
# toy appears in borrowed displayed toys list
# user selects borrow duration - toy fee in list adjusts
# on fee being collected, done commits new toys to DB



def borrow(request, member_id):
    context = {}


    # TODO retrieve from elsewhere
    # base page context
    context.update({"daily_balance": 23.20, "login_name": "Jess Benning"})

    # display toy in toy summary
    context.update(handle_toy_summary(request))

    # handle member search
    context.update(handle_member_search(request))

    # if member_id set display member summary and list of borrowed toys
    if (member_id):
        context.update(handle_member_summary(request, member_id))
        context.update(handle_borrowed_toy_list(request, member_id))

    # Always need this so search box renders
    context.update(handle_toy_borrow(request, member_id))

    new_borrow_list = TempBorrowList.objects.filter(member=member_id)
    context.update({"new_borrow_list": new_borrow_list})

    context.update(handle_payment_form(request, member_id))
    print(context)
    return render(request, 'toybox/borrow.html', context)


# also adds toy to temp list in DB via POST
def handle_toy_borrow(request, member_id):
    toys = None
    error = ""
    toycode = ""

    form = ToySearchForm(request.POST)

    if (request.method == "POST"):
        print("POST")
        if form.is_valid():
            if "add_toy" in request.POST:
                toycode = form.cleaned_data['toy_id']
                form = ToySearchForm(request.POST, initial={"toy_id": toycode})

                if toycode == "":
                    error = "Toy code not entered"
                else:

                    toy = Toy.objects.filter(code__iexact=toycode)

                    #print("SERACH " + toycode + ": " + str(toy.count()))

                    if toy.count() > 0:
                        if toy[0].state != Toy.AT_TOY_LIBRARY:
                            error = "Toy set to unavailable"
                        else:
                            in_temp_list = TempBorrowList.objects.filter(toy=toy[0])

                            if not in_temp_list:
                                member = get_object_or_404(Member, pk=member_id)
                                tempBorrowList = TempBorrowList()
                                tempBorrowList.store(member, toy[0])
                            else:
                                error = "Toy on loan"
                    else:
                        error = "Toy not found"
                        if (member_id):
                            if (Toy.objects.filter(member_loaned=member_id, code=toycode).count() > 0):
                                error = "Toy on loan"

                if error != "":
                    form.add_error("toy_id", error)
        else:
            print("toy borrow form not valid")

    elif request.method == "GET":
        toycode = request.GET.get('tc')

    if form.is_valid() and toycode:
        toys = get_list_or_404(Toy, code__iexact=toycode)

    context = {'toy_search_form': form, 'toys': toys}

    return context


def handle_payment_form(request, member_id):
    # TODO update member balance and transaction table
    # TODO update toy loan duration
    context = {}
# TODO store default duration in settings. Request.POST here ruins initial data
    #payment_form = PaymentForm(request.POST)#initial={'loan_duration':'2'})#request.POST)

    if (request.method == "POST"):
        payment_form = PaymentForm(request.POST)
        # print("posted")

        new_borrow_list = TempBorrowList.objects.filter(member=member_id)

        for item in request.POST:
            #print(item)
            if item.startswith("remove_toy_"):
                toy_to_remove = item[len("remove_toy_"):]
                # print("REMOVE TOY: "+toy_to_remove)
                TempBorrowList.objects.filter(toy__code=toy_to_remove, member__id=member_id).delete()

            if item == "done":


                if payment_form.is_valid():
                    # print("valid form")
                    member = get_object_or_404(Member, pk=member_id)

                    for new_toy in new_borrow_list:
                        loan_duration = payment_form.cleaned_data['loan_duration']
                        # print("LOAN_DURATION: "+loan_duration)
                        toy = get_object_or_404(Toy, code=new_toy.toy.code)
                        toy.borrow_toy(member, int(loan_duration))
                        TempBorrowList.objects.filter(toy__code=new_toy.toy.code, member__id=member_id).delete()

                    try:
                        fee_due = decimal.Decimal(payment_form.cleaned_data['fee_due'])
                    except:
                        due_error = "Not a number"
                        # print(payment_form.cleaned_data['fee_due']," ",due_error)
                        break

                    print("Due " + str(fee_due))
                    # TODO add error message
                    try:
                        fee_paid = decimal.Decimal(payment_form.cleaned_data['fee_paid'])
                    except:
                        paid_error = "Not a number"
                        # print(payment_form.cleaned_data['fee_paid']," ",paid_error)
                        break

                    # print("Paid "+str(fee_paid))
                    # TODO create transaction record
                    # print(member.balance)
                    member.balance = member.balance - fee_due + fee_paid
                    print(member.balance)
                    member.save()

    payment_form = PaymentForm(initial={'loan_duration':'2'})

    context.update({'payment_form': payment_form})

    # print(context)
    return context


class PaymentForm(forms.Form):
    numeric = RegexValidator(r'^[0-9.]*$', 'Only numeric characters are allowed.')
    # TODO store loan durations options in settings
    LOAN_DURATIONS = "126"
    LOAN_CHOICES = []

    # so choices can be easily stored in settings
    for c in LOAN_DURATIONS:
        LOAN_CHOICES.append((c, c))

    loan_duration = forms.ChoiceField(choices=LOAN_CHOICES, widget=forms.RadioSelect())
    fee_due = forms.CharField(label="Fee Due", max_length=20, validators=[numeric])
    fee_paid = forms.CharField(label="Fee Paid", max_length=20, validators=[numeric])

