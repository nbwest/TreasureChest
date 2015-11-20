from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from shared import *
from django.db.models import *
from django.core.validators import *
from django.utils.safestring import mark_safe
from datetime import *
import decimal

# TODO limit toys to four - number is stored in DB



# work flow
# member is searched for and once selected displays user stats
# existing borrowed toys appear in toy list - these can't be removed and there are no fees
# User enters a toy to be borrowed
# if available then toy appears in borrowed displayed toys list else an error appears
# user selects borrow duration - toy fee in list adjusts
# borrow fee is displayed
# Other fees
# fee is collected and entered into the actual fee field
# Asks member if they want change, to donate or use as credit
#



def borrow(request, member_id):
    context = {}


    # TODO retrieve from elsewhere
    # base page context
    context.update({"daily_balance": 23.20, "login_name": "Jess Benning"})

    context.update(handle_payment_form(request, member_id))

    # handle member search
    context.update(handle_member_search(request))

    # print(context)
    # Always need this so search box renders
    context.update(handle_toy_borrow(request, member_id, ("toy_removed" in context)))

    new_borrow_list = TempBorrowList.objects.filter(member=member_id)

    new_borrow_toy_list=[]
    for item in new_borrow_list:
        new_borrow_toy_list.append(item.toy)

    context.update({"new_borrow_toy_list": new_borrow_toy_list})


     # if member_id set display member summary and list of borrowed toys
    if (member_id):
        context.update(handle_member_summary(request, member_id))
        context.update(handle_borrowed_toy_list(request, member_id))


    # print(context)

    if "clear_form" in context:
        context.pop("toy_list",None)
        context.pop("member",None)
        context.pop("new_borrow_toy_list",None)

    return render(request, 'toybox/borrow.html', context)


# also adds toy to temp list in DB via POST
def handle_toy_borrow(request, member_id, ignore_error):
    toy_search_results = None
    toy=None
    error = ""
    toy_search_string = ""
    form = None

    #need here for toy search to render
    form = ToySearchForm(request.POST)

    #from toy search
    if (request.method == "POST"):
        if form.is_valid():
            #from toy search
            if "search_toy" in request.POST:
                toy_search_string = form.cleaned_data['toy_search_string'].strip()
                if toy_search_string != "":
                    toy_search_results=Toy.objects.filter(Q(code__iexact=toy_search_string)|Q(name__contains=toy_search_string)).order_by("code")
                    if toy_search_results.count() == 1:
                        toy=toy_search_results[0]
                    elif toy_search_results.count() == 0:
                        error = "Toy not found"
                else:
                    error = "Toy code not entered"
                #from modal dialog toy select
            elif "select_toy" in request.POST:
                toy_id=request.POST['select_toy'].strip()
                toy=get_object_or_404(Toy, id=toy_id)

            if toy:
                    if toy.state == Toy.ON_LOAN:
                        error = "Toy on loan"
                    elif toy.state == Toy.BEING_REPAIRED:
                        error = "Toy is being repaired"
                    elif toy.state == Toy.TO_BE_REPAIRED:
                        error = "Toy is due for repair"
                    elif toy.state == Toy.STOCKTAKE:
                        error = "Toy needs stocktaking and can't be borrowed"
                    elif toy.state == Toy.RETIRED:
                        error = "ERROR - Toy is retired!"
                    elif toy.state == Toy.AVAILABLE:
                        #available, check it hasn't alredy been borrowed already
                        in_temp_list = TempBorrowList.objects.filter(toy=toy)

                        if not in_temp_list:
                            #OK to add to temp borrow list
                            member = get_object_or_404(Member, pk=member_id)
                            tempBorrowList = TempBorrowList()
                            tempBorrowList.store(member, toy)
                        else:
                            error = "Toy already borrowed"

                    else:
                        error = "Toy state invalid, toy id: "+toy.id+", toy state: "+toy.state
                       #TODO log in feedback

            else:
                 error = ""#Toy invalid, search: "+toy_search_string
                #TODO log in feedback



            if error != "" and not ignore_error:
                form.add_error("toy_search_string", error)
            else:
                form.initial.update({"toy_search_string":""})
                #research below
                #return http.HttpResponseRedirect('')


    context = {'toy_search_form': form, 'toy_search_results': toy_search_results, 'toy':toy}

    return context




def handle_payment_form(request, member_id):
    # TODO update member balance and transaction table
    # TODO update toy loan duration
    context = {}

    #payment_form = PaymentForm(request.POST)#initial={'loan_duration':'2'})#request.POST)

    if (request.method == "POST"):
        payment_form = PaymentForm(request.POST)


        new_borrow_list = TempBorrowList.objects.filter(member=member_id)

        for item in request.POST:
            #print(item)
            if item.startswith("remove_toy_"):
                toy_to_remove = item[len("remove_toy_"):]
                # print("REMOVE TOY: "+toy_to_remove)
                TempBorrowList.objects.filter(toy__id=toy_to_remove, member__id=member_id).delete()
                context.update({"toy_removed":True})

            #TODO Add donate and return change options
            # donate adds a different transaction and doesn't go to their credit
            # return change same as exact
            if item == "exact" or item=="credit" or item=="donate" or item=="return":
                if payment_form.is_valid():
                    print("valid form")
                    member = get_object_or_404(Member, pk=member_id)

                    if new_borrow_list.count()>0:
                        for new_toy in new_borrow_list:
                            loan_duration = payment_form.cleaned_data['loan_duration']
                            print("LOAN_DURATION: "+loan_duration)
                            toy = get_object_or_404(Toy, id=new_toy.toy.id)
                            print(toy)
                            toy.borrow_toy(member, int(loan_duration))
                            remove_toys_temp=TempBorrowList.objects.filter(toy__id=new_toy.toy.id, member__id=member_id)
                            remove_toys_temp.delete()

                        try:
                            fee_due = decimal.Decimal(payment_form.cleaned_data['total_fee'])
                        except:
                            due_error = "Not a number"
                            # print(payment_form.cleaned_data['fee_due']," ",due_error)
                            break

                        print("Due " + str(fee_due))
                        # TODO add error message
                        try:
                            fee_paid = decimal.Decimal(payment_form.cleaned_data['payment'])
                        except:
                            paid_error = "Not a number"
                            print(payment_form.cleaned_data['fee_paid']," ",paid_error)
                            break

                        print("Paid "+str(fee_paid))

                        print(member.balance)
                        #TODO bring in other fee types, each one has their own transaction?
                        transaction_type=Transaction.HIRE_CHARGE
                        #TODO create transaction record for hire change
                        transaction=Transaction()
                        transaction.create_transaction_record(member,transaction_type,fee_paid,None)

                        if item=="credit":
                            member.balance = member.balance - fee_due + fee_paid
                            print(member.balance)
                            member.save()
                            transaction_type=Transaction.CREDIT_ADJUSTMENT

                            transaction.create_transaction_record(member,transaction_type,fee_paid-fee_due,None)
                            #TODO add additional transaction record
                        elif item=="donate":
                            transaction_type=Transaction.DONATION
                            transaction.create_transaction_record(member,transaction_type,fee_paid-fee_due,None)
                            #TODO add additional transaction record



                        context.update({"clear_form":True})

                else:
                     print("invalid form " + str(payment_form.errors))

    try:
        default_loan_duration = Config.objects.get(key="default_loan_duration").value
    except Config.DoesNotExist:
        default_loan_duration = "2"

    # TODO Request.POST here ruins initial data
    #payment_form = PaymentForm(request.POST,initial={'loan_duration':'2'})
    #including request.POST clears initial data, without it validation errors are missing
    payment_form = PaymentForm(initial={'loan_duration':default_loan_duration, 'late_fee':0, 'membership':0, 'issue_fee':0, 'bond_fee':0})

    # if form charfield has an amount in it make it visible.
    for field in payment_form:
        if field.html_name in payment_form.initial and field.field.__class__.__name__=="CharField":
            if float(payment_form.initial[field.html_name]) != 0:
                    field.field.widget.attrs.update({'visible':'True'})

        #
        # print field.html_name
        # print field.field.widget.attrs
        # print field.field.__class__.__name__
        # print



    context.update({'payment_form': payment_form})

    # print(context)
    return context


class PaymentForm(forms.Form):
    numeric = RegexValidator(r'^[0-9.]*$', 'Only numeric characters are allowed.')

    try:
        loan_durations = Config.objects.get(key="loan_durations").value
    except Config.DoesNotExist:
        loan_durations = "12"

    loan_choices = []
    # so choices can be easily stored in settings
    for c in loan_durations:
        loan_choices.append((c, c))

    loan_duration = forms.ChoiceField(label="Loan duration in weeks",choices=loan_choices, widget=forms.RadioSelect())

    borrow_fee = forms.CharField(label="Borrow Fee", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'total_me':'true','readonly':'readonly', 'adjust_button':'True','visible':'True'}))
    late_fee = forms.CharField(required=False, label="Late Fee", max_length=20, validators=[numeric], widget=forms.TextInput(attrs={'total_me':'true','readonly':'readonly', 'adjust_button':'True'}))
    issue_fee = forms.CharField(required=False, label="Issue Fee", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'total_me':'true','readonly':'readonly', 'adjust_button':'True'}))
    bond_fee = forms.CharField(required=False, label="Bond Fee", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'total_me':'true','readonly':'readonly', 'adjust_button':'True'}))
    membership = forms.CharField(required=False, label="Membership", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'total_me':'true','readonly':'readonly', 'adjust_button':'True'}))
    donation = forms.CharField(required=False, label="Donation", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'total_me':'true','visible':'True'}))
    total_fee = forms.CharField(label="Total", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'hr':'True','visible':'True','readonly':'readonly'}))
    payment = forms.CharField(label="Payment", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'hr':'True', 'visible':'True'}))
    change = forms.CharField(label="Change", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'visible':'True','readonly':'readonly', 'change_buttons':'True'}))


