from django.shortcuts import render
from shared import *
from django.db.models import *
from django.core.validators import *
from django.shortcuts import redirect

import decimal
from django.contrib.auth.decorators import login_required


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


@login_required
def borrow(request, member_id):
    context = {}


    context.update(base_data(request))

    #clears templist if there are temp toys in any other name than the current member. Ensures temp toys
    # aren't persistent when leaving borrow page
    if TempBorrowList.objects.exclude(member=member_id).count()>0:
        TempBorrowList.objects.all().delete()


    # handle member search
    context.update(handle_member_search(request))


    # Always need this so search box renders. Handles borrowing a toy
    context.update(handle_toy_borrow(request, member_id, ("toy_removed" in context)))

    # handle payments, toy removal and repair loan
    context.update(handle_payment_form(request, member_id))


     # if member_id set display member summary and list of borrowed toys
    if (member_id):
        context.update(handle_member_summary(request, member_id))
        context.update(handle_borrowed_toy_list(request, member_id))
    else:
        context["member_search_form"].fields["member_name_fragment"].widget.attrs.update({"autofocus":"true"})


    if "clear_form" in context:
         return redirect('/toybox/borrow/')
    else:
        return render(request, 'toybox/borrow.html', context)


# also adds toy to temp list in DB via POST
def handle_toy_borrow(request, member_id, ignore_error):
    toy_search_results = None
    toy=None
    error = ""

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

                    temp_list_count=TempBorrowList.objects.filter(member__id=member_id).exclude(toy__state=Toy.TO_BE_REPAIRED).count()+1
                    prev_borrow_count=Toy.objects.filter(member_loaned=member_id).count()

                    try:
                        max_toys = int(Config.objects.get(key="max_toys").value)
                    except Config.DoesNotExist:
                        max_toys = 10

                    if temp_list_count+prev_borrow_count > max_toys:
                        error="Toy borrow limit reached"
                    elif toy.state == Toy.ON_LOAN:
                        error = "Toy on loan"
                    elif toy.state == Toy.BEING_REPAIRED:
                        error = "Toy is being repaired"
                    elif toy.state == Toy.STOCKTAKE:
                        error = "Toy needs stocktaking and can't be borrowed"
                    elif toy.state == Toy.RETIRED:
                        error = "ERROR - Toy is retired!"
                    elif toy.state == Toy.AVAILABLE or toy.state == Toy.TO_BE_REPAIRED:
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
                        error = "Toy state invalid, toy id: "+str(toy.id)+", toy state: "+str(toy.state)



            if error != "" and not ignore_error:
                form.add_error("toy_search_string", error)
            else:
                #reset form
                form = ToySearchForm()


    if member_id:
        form.fields["toy_search_string"].widget.attrs.update({"autofocus":"true"})

    context = {'toy_search_form': form, 'toy_search_results': toy_search_results, 'toy':toy}

    return context


# def perform_transaction(member,form,id,transaction_type):
#     if id in form.cleaned_data:
#         if form.cleaned_data[id]!="":
#             fee=decimal.Decimal(form.cleaned_data[id])
#             if fee!=0:
#                 if id+"_adjust_justification" in form.cleaned_data:
#                     if form.cleaned_data[id+"_adjust_justification" ]!="":
#                         comment="ADJ: "+form.cleaned_data[id+"_adjust_justification" ]
#                     else:
#                         comment=None
#                 transaction=Transaction()
#                 transaction.create_transaction_record(request.user,member,transaction_type,fee,comment)
#                 return transaction


def handle_payment_form(request, member_id):

    context = {}
    member=None


    if member_id:
        member = get_object_or_404(Member, pk=member_id)

    try:
        repair_loan_duration = Config.objects.get(key="repair_loan_duration").value
    except Config.DoesNotExist:
        repair_loan_duration = "26"

    context.update({"repair_loan_duration":repair_loan_duration})

    if (request.method == "POST"):

        new_borrow_list = TempBorrowList.objects.filter(member=member_id)
        payment_form = PaymentForm(request.POST,temp_toy_list=new_borrow_list)

        if "cancel" in request.POST:
            context.update({"clear_form":True})

        elif member:
            #check remove toy submit action
            for item in request.POST:
                if item.startswith("remove_toy_"):
                    toy_to_remove = item[len("remove_toy_"):]
                    TempBorrowList.objects.filter(toy__id=toy_to_remove, member__id=member_id).delete()
                    context.update({"toy_removed":True})




            if payment_form.is_valid():

                #check for submit action
                if any(k in ("exact","add_credit","donate","return","use_credit") for k in request.POST):


                    #Assign borrowed toys to member if any
                    for new_toy in new_borrow_list:
                        loan_duration = payment_form.cleaned_data['loan_duration']
                        # if payment_form.cleaned_data['loan_duration']
                        print("LOAN_DURATION: "+loan_duration)
                        toy = get_object_or_404(Toy, id=new_toy.toy.id)

                        loaned_for_repair=False

                        if "repair_checkbox_"+str(toy.id) in payment_form.cleaned_data:
                            if payment_form.cleaned_data["repair_checkbox_"+str(toy.id)]:

                                loaned_for_repair=True
                                loan_duration=repair_loan_duration

                        print(toy)
                        toy.borrow_toy(member, int(loan_duration),request.user, loaned_for_repair)
                        remove_toys_temp=TempBorrowList.objects.filter(toy__id=new_toy.toy.id, member__id=member_id)
                        remove_toys_temp.delete()



                    #borrow fee transaction
                    if "borrow_fee" in payment_form.cleaned_data:
                        if payment_form.cleaned_data['borrow_fee']!="":
                            fee=decimal.Decimal(payment_form.cleaned_data['borrow_fee'])
                            if fee!=0:
                                if "borrow_fee_adjust_justification" in payment_form.cleaned_data:
                                    if payment_form.cleaned_data['borrow_fee_adjust_justification']!="":
                                        comment=payment_form.cleaned_data['borrow_fee_adjust_justification']
                                    else:
                                        comment=None
                                transaction=Transaction()
                                transaction.create_transaction_record(request.user,member,Transaction.BORROW_FEE,fee,comment)

                    #membership fee transaction
                    if "membership" in payment_form.cleaned_data:
                        if payment_form.cleaned_data['membership']!="":
                            fee=decimal.Decimal(payment_form.cleaned_data['membership'])
                            if fee!=0:
                                if "borrow_fee_adjust_justification" in payment_form.cleaned_data:
                                    if payment_form.cleaned_data['membership_adjust_justification']!="":
                                        comment=payment_form.cleaned_data['membership_adjust_justification']
                                    else:
                                        comment=None

                                transaction=Transaction()
                                transaction.create_transaction_record(request.user,member,Transaction.MEMBERSHIP_FEE,fee,comment)

                                member.update_membership_date()


                    #TODO toy deposit fee - also add new transaction choice

                    #Member deposit fee transaction
                    if "deposit_fee" in payment_form.cleaned_data:
                        if payment_form.cleaned_data['deposit_fee']!="":
                            fee=decimal.Decimal(payment_form.cleaned_data['deposit_fee'])
                            if fee!=0:
                                if "deposit_fee_adjust_justification" in payment_form.cleaned_data:
                                    if payment_form.cleaned_data['deposit_fee_adjust_justification']!="":
                                        comment=payment_form.cleaned_data['deposit_fee_adjust_justification']
                                    else:
                                        comment=None
                                transaction=Transaction()
                                transaction.create_transaction_record(request.user,member,Transaction.MEMBER_DEPOSIT,fee,comment)
                                member.deposit_fee_paid=fee
                                member.save()


                    #overdue fee transaction completion
                    if "late_fee" in payment_form.cleaned_data:
                        if payment_form.cleaned_data['late_fee']!="":
                            fee=decimal.Decimal(payment_form.cleaned_data['late_fee'])
                            if fee!=0:
                                if "late_fee_adjust_justification" in payment_form.cleaned_data:
                                    if payment_form.cleaned_data['late_fee_adjust_justification']!="":
                                        comment=payment_form.cleaned_data['late_fee_adjust_justification']
                                    else:
                                        comment=None
                                fees_records=Transaction.objects.filter(complete=False, member__id=member_id, transaction_type=Transaction.LATE_FEE)

                                for item in fees_records:
                                    # transaction=Transaction()
                                    # transaction.create_transaction_record(request.user,member,Transaction.LATE_FEE,fee,comment)
                                    item.amount=fee
                                    item.comment=comment
                                    item.complete=True
                                    item.save()

                    if "issue_fee" in payment_form.cleaned_data:
                        if payment_form.cleaned_data['issue_fee']!="":
                            fee=decimal.Decimal(payment_form.cleaned_data['issue_fee'])
                            if fee!=0:
                                if "issue_fee_adjust_justification" in payment_form.cleaned_data:
                                    if payment_form.cleaned_data['issue_fee_adjust_justification']!="":
                                        comment=payment_form.cleaned_data['issue_fee_adjust_justification']
                                    else:
                                        comment=None

                                fees_records=Transaction.objects.filter(complete=False, member__id=member_id, transaction_type=Transaction.ISSUE_FEE)

                                for item in fees_records:
                                    # transaction=Transaction()
                                    # transaction.create_transaction_record(request.user,member,Transaction.ISSUE_FEE,fee,comment)
                                    item.amount=fee
                                    item.comment=comment
                                    item.complete=True
                                    item.save()


                    if "change" in payment_form.cleaned_data:
                        if payment_form.cleaned_data['change']!="":
                            change=decimal.Decimal(payment_form.cleaned_data['change'])
                            # if fee!=0:
                            #     transaction=Transaction()
                            #     transaction.create_transaction_record(request.user,member,Transaction.CHANGE,fee)

                    if "payment" in payment_form.cleaned_data:
                        if payment_form.cleaned_data['payment']!="":
                            fee=decimal.Decimal(payment_form.cleaned_data['payment'])
                            fee_paid=fee
                            if fee!=0:
                                transaction=Transaction()
                                transaction.create_transaction_record(request.user,member,Transaction.PAYMENT,fee)

                    #TODO enable donation
                    # if "donation" in payment_form.cleaned_data:
                    #     if payment_form.cleaned_data['donation']!="":
                    #         fee=decimal.Decimal(payment_form.cleaned_data['donation'])
                    #         if fee!=0:
                    #             transaction=Transaction()
                    #             transaction.create_transaction_record(request.user,member,Transaction.MEMBER_DONATION,fee)

                    #issue fee transation completion


                    context.update({"clear_form":True})



                    if "total_fee" in payment_form.cleaned_data:
                        if payment_form.cleaned_data['total_fee']!="":
                            fee_due = decimal.Decimal(payment_form.cleaned_data['total_fee'])

                    #look at submit actions
                    for item in request.POST:

                        if item=="add_credit":

                            if change>0: #add credit
                                member.balance = member.balance - fee_due + fee_paid
                                print(member.balance)
                                member.save()
                                transaction=Transaction()
                                transaction.create_transaction_record(request.user,member,Transaction.MEMBER_CREDIT,fee_paid-fee_due,balance_change=fee_paid)
                                break
                            else:
                                member.balance = member.balance - fee_due
                                member.save()
                                transaction=Transaction()
                                transaction.create_transaction_record(request.user,member,Transaction.MEMBER_DEBIT,fee_due)
                                break



                        elif item=="donate":
                            transaction=Transaction()
                            transaction.create_transaction_record(request.user,member,Transaction.MEMBER_DONATION,fee_paid-fee_due,balance_change=fee_paid)
                            break

                        elif item=="return":
                            transaction=Transaction()
                            transaction.create_transaction_record(request.user,member,Transaction.CHANGE,fee_paid-fee_due,balance_change=fee_due)
                            break

                        elif item=="exact":
                            transaction=Transaction()
                            transaction.create_transaction_record(request.user,member,Transaction.CHANGE,0,balance_change=fee_due)
                            break

            else:
                print("invalid form " + str(payment_form.errors))



    # fill in default loan duration
    try:
        default_loan_duration = Config.objects.get(key="default_loan_duration").value
    except Config.DoesNotExist:
        default_loan_duration = "2"

    #fill in other fees

    #TODO toy deposit
    balance=0
    late_fee=0
    issue_fee=0
    membership_fee=0
    deposit_fee=0

    if member and not "clear_form" in context:
        balance=member.balance
        late_fees_records=Transaction.objects.filter(complete=False, member__id=member_id, transaction_type=Transaction.LATE_FEE)
        late_fee=sum(f.amount for f in late_fees_records)

        issue_fees_records=Transaction.objects.filter(complete=False, member__id=member_id, transaction_type=Transaction.ISSUE_FEE)
        issue_fee=sum(f.amount for f in issue_fees_records)

        if not member.membership_valid():
            membership_fee=member.type.fee

        if not member.deposit_paid():
            deposit_fee=member.type.deposit

    new_borrow_list=TempBorrowList.objects.filter(member=member_id)
    payment_form = PaymentForm(temp_toy_list=new_borrow_list,initial={'loan_duration':default_loan_duration, 'late_fee':late_fee, 'membership':membership_fee, 'issue_fee':issue_fee, 'deposit_fee':deposit_fee, 'credit':balance})

    # if form charfield has an amount in it make it visible.
    for field in payment_form:
        if field.html_name in payment_form.initial and field.field.__class__.__name__=="CharField":
            if float(payment_form.initial[field.html_name]) != 0:
                    field.field.widget.attrs.update({'enabled':'True'})


    #make borrow toys query result into a list of toys
    new_borrow_toy_list=[]
    for item in new_borrow_list:
        new_borrow_toy_list.append(item.toy)

    context.update({'payment_form': payment_form,"new_borrow_toy_list": new_borrow_toy_list})


    return context



class PaymentForm(forms.Form):


    def __init__(self, *args, **kwargs):
        toyList=kwargs.pop("temp_toy_list", 0)
        super(PaymentForm, self).__init__(*args, **kwargs)

        if toyList:
            for toy in toyList:
                self.fields['repair_checkbox_%s' % toy.toy.id]=forms.BooleanField(required=False)

    numeric = RegexValidator(r'^[0-9.]*$', 'Only numeric characters are allowed.')

    try:
        loan_durations = Config.objects.get(key="loan_durations").value
    except Config.DoesNotExist:
        loan_durations = "12"

    loan_choices = []
    # so choices can be easily stored in settings
    for c in loan_durations:
        loan_choices.append((c, c))

    #ensure any input with adjust button also has a justification field with suffix of _adjust_justification with its name

    loan_duration = forms.ChoiceField(label="Loan duration in weeks",choices=loan_choices, widget=forms.RadioSelect())

    borrow_fee = forms.CharField(label="Borrow Fee", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'total_me':'true','readonly':'readonly', 'adjust_button':'True','enabled':'True'}))
    borrow_fee_adjust_justification = forms.CharField(required=False, max_length=100,widget=forms.HiddenInput(attrs={'type':'hidden','enabled':'True'}))

    late_fee = forms.CharField(required=False, label="Late Fee", max_length=20, validators=[numeric], widget=forms.TextInput(attrs={'total_me':'true','readonly':'readonly','adjust_button':'True'}))
    late_fee_adjust_justification = forms.CharField(required=False, max_length=100,widget=forms.HiddenInput(attrs={'type':'hidden','enabled':'True'}))

    issue_fee = forms.CharField(required=False, label="Issue Fee", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'total_me':'true','readonly':'readonly','adjust_button':'True'}))
    issue_fee_adjust_justification = forms.CharField(required=False, max_length=100,widget=forms.HiddenInput(attrs={'type':'hidden','enabled':'True'}))

    deposit_fee = forms.CharField(required=False, label="Deposit Fee", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'total_me':'true','readonly':'readonly', 'adjust_button':'True'}))
    deposit_fee_adjust_justification = forms.CharField(required=False, max_length=100,widget=forms.HiddenInput(attrs={'type':'hidden','enabled':'True'}))

    membership = forms.CharField(required=False, label="Membership", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'total_me':'true','readonly':'readonly', 'adjust_button':'True'}))
    membership_adjust_justification = forms.CharField(required=False, max_length=100,widget=forms.HiddenInput(attrs={'type':'hidden','enabled':'True'}))
    #TODO enable donation
    # donation = forms.CharField(required=False, label="Donation", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'total_me':'true','enabled':'True'}))
    credit = forms.CharField(label="Credit", max_length=50, widget=forms.TextInput(attrs={'hr':'True','enabled':'True','readonly':'readonly'}))
    total_fee = forms.CharField(label="Total", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'enabled':'True','readonly':'readonly'}))

    payment = forms.CharField(label="Payment", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'hr':'True', 'enabled':'True', 'cancel_button':'True'}))
    change = forms.CharField(label="Change", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'enabled':'True','readonly':'readonly', 'change_buttons':'True'}))


