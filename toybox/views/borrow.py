from django.shortcuts import render
from shared import *
from django.db.models import *
from django.core.validators import *
from datetime import datetime
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages

import decimal
from django.contrib.auth.decorators import login_required
import member_edit
import json


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
    context={}

    rendered = render_ajax_request(request)
    if rendered != None:
        return rendered

    rendered = member_edit.render_ajax_request(request)
    if rendered != None:
        return rendered

    # if request.method == "POST":
    #    context=member_edit.handle_member_edit(request, member_id)

    if request.method=="POST" and request.is_ajax():
        # if "page_leave_check" in request.session:
        #     context.update({"leave_check":True})
        # else
        # request.session.pop("page_leave_check", None)
        context.update(member_edit.handle_member_edit(request,member_id))
        rendered = render_to_string('toybox/member_edit.html', context)
        context.update({"member_edit_form":rendered})
        return HttpResponse(json.dumps(context))


    context.update({"title":"Borrow Toy & Payment"})

    context.update(base_data(request))

 #TODO check volunteers set borrow fee to zero. include message under borrow fee

    #clears templist if there are temp toys in any other name than the current member. Ensures temp toys
    # aren't persistent when leaving borrow page
    # this means only one member can be serviced at a time. optional???
    #if TempBorrowList.objects.exclude(member=member_id).count()>0:
     #   TempBorrowList.objects.filter().delete()


    handle_quarantine(request, member_id)

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
        request.session.update({"page_leave_check": True})
    else:
        context["member_search_form"].fields["member_name_fragment"].widget.attrs.update({"autofocus":"true"})

    if "clear_form" in context:
        # context.pop("toy_list",None)
        # context.pop("member",None)
        # context.pop("toy_search_results",None)
        # context.pop("toy",None)
        # context.pop("new_borrow_toy_list",None)
        #
        # if "payment_form" in context and "payment" in context["payment_form"].errors:
        #     context["payment_form"].errors.pop('payment')
        #
        # # pf.errors['payment'] = pf.error_class()
        #
        #
        # # context.update({"payment_form": pf})
        # request.path_info=u'/toybox/borrow/'
        # request.path=request.path_info
        # request.session.pop("page_leave_check",None)
        if "success" in context:
            messages.add_message(request, messages.SUCCESS, "Transaction Successful")
        return redirect(reverse("toybox:borrow"))


        # save any changes to toy fields
        # remove toy - removes all new toys
        # new_borrow_toy_list = []
        # for item in tempBorrowList:
        #     new_borrow_toy_list.append(item.toy)
        # handle_toy_details_form(request, new_borrow_toy_list)


    return render(request, 'toybox/borrow.html', context)

def handle_quarantine(request,member_id):
    if (request.method == "POST"):
        if "quarantine_toy" in request.POST:
            toy_id=request.POST["quarantine_toy"]
            if toy_id != None:

                temp_list = TempBorrowList.objects.filter(toy__id=toy_id,member__id=member_id)

                new_borrow_toy_list = []
                for item in temp_list:
                    new_borrow_toy_list.append(item.toy)

                handle_toy_details_form(request, new_borrow_toy_list)


                TempBorrowList.objects.filter(toy__id=toy_id, member__id=member_id).delete()

    return None


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




                    toy_search_results=Toy.objects.filter(Q(code__iexact=toy_search_string)|Q(name__icontains=toy_search_string)).order_by("state")

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



                    max_toys = int(get_config("max_toys"))


                    if temp_list_count+prev_borrow_count > max_toys:
                        error="Toy borrow limit reached"
                    elif toy.state == Toy.ON_LOAN:
                        error = "Toy on loan"
                    elif toy.state == Toy.BEING_REPAIRED:
                        error = "Toy is being repaired"
                    elif toy.state == Toy.STOCKTAKE:
                        error = "Toy needs stocktaking and can't be borrowed"
                    elif toy.state == Toy.RETIRED:
                        error = "Toy is retired"
                    elif toy.state == Toy.TO_BE_RETIRED:
                        error = "Toy is awaiting inspection for retirement"
                    elif toy.state == Toy.MISSING:
                        error = "Toy is missing"
                    elif toy.state == Toy.TO_BE_REPAIRED:
                        error = "Toy is broken and needs repair"
                    elif toy.state == Toy.TO_BE_CATALOGED:
                        error = "Toy is not ready to be lent out - To be cataloged"
                    elif toy.state == Toy.AVAILABLE or toy.state == Toy.TO_BE_REPAIRED:
                        #available, check it hasn't alredy been borrowed already
                        in_temp_list = TempBorrowList.objects.filter(toy=toy,member__id=member_id)

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

    context = {'toy_search_form': form, 'toy_search_results': toy_search_results, 'new_toy':toy, }


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
    adjustment_found=False
    payment_form=None
    volunteer = False
    comment=None


    if member_id:
        member = get_object_or_404(Member, pk=member_id)

    if member_id:
        try:
            Shift.objects.get(volunteer=member_id, shift_date=thisDateTime().date())
            volunteer=True
        except:
            pass

    credit_enable = get_config("credit_enable")
    repair_loan_duration = get_config("repair_loan_duration")
    loan_bond_enable= get_config("loan_bond_enable")
    donation_enable=get_config("donation_enable")

    context.update({"repair_loan_duration":repair_loan_duration,"credit_enable":credit_enable,"loan_bond_enable":loan_bond_enable,"donation_enable":donation_enable})
    new_borrow_list = TempBorrowList.objects.filter(member__id=member_id)

    if (request.method == "POST"):

#not saving on adding new toy after previus toy comments changed

            if "cancel" in request.POST:
                context.update({"clear_form":True})
                TempBorrowList.objects.all().delete()

            elif member and "remove_toy" in request.POST:
                #check remove toy submit action
                toy_to_remove = request.POST["remove_toy"]
                TempBorrowList.objects.filter(toy__id=toy_to_remove, member__id=member_id).delete()
                context.update({"toy_removed":True})
                new_borrow_list = TempBorrowList.objects.filter(member__id=member_id)

            elif member:
                payment_form = PaymentForm(request.POST, temp_toy_list=new_borrow_list)
                if payment_form.is_valid():

                    #check for submit action
                    # if any(k in ("exact","add_credit","donate","return","use_credit") for k in request.POST):
                    if any(k in ("paid","add_credit","donate","return") for k in request.POST):




                        transaction=Transaction()
                        #borrow fee transaction
                        if "borrow_fee" in payment_form.cleaned_data:
                            if payment_form.cleaned_data['borrow_fee']!="":
                                fee=decimal.Decimal(payment_form.cleaned_data['borrow_fee'])

                                if payment_form.cleaned_data['borrow_fee_adjust_justification']!="":
                                    comment=payment_form.cleaned_data['borrow_fee_adjust_justification']
                                    adjustment_found=True
                                else:
                                    comment=None

    #TODO ISSUE borrow fee justification comment isn't being set unless the adjust is clicked. Also adjust original value is zero
                                if fee!=0 or comment is not None:
                                    transaction.create_transaction_record(request.user,member,Transaction.BORROW_FEE,fee,comment)


                        #Assign borrowed toys to member if any
                        for new_toy in new_borrow_list:
                            loan_duration = payment_form.cleaned_data['loan_duration']

                            # if payment_form.cleaned_data['loan_duration']
                           # print("LOAN_DURATION: "+loan_duration)
                            toy = get_object_or_404(Toy, id=new_toy.toy.id)

                            loaned_for_repair=False

                            if "repair_checkbox_"+str(toy.id) in payment_form.cleaned_data:
                                if payment_form.cleaned_data["repair_checkbox_"+str(toy.id)]:
                                    loaned_for_repair=True
                                    loan_duration=repair_loan_duration

                            # print(toy)
                            borrow_datetime_from_form=payment_form.cleaned_data['borrow_date']

                            if borrow_datetime_from_form==thisDateTime().date():
                                borrow_datetime = thisDateTime()
                            else:
                                borrow_datetime = datetime(borrow_datetime_from_form.year,borrow_datetime_from_form.month,borrow_datetime_from_form.day,0,0,0)

                            toy.borrow_toy(member, int(loan_duration),request.user, loaned_for_repair, transaction, borrow_datetime)
                            remove_toys_temp=TempBorrowList.objects.filter(toy__id=new_toy.toy.id, member__id=member_id)
                            remove_toys_temp.delete()

                        #membership fee transaction
                        if "membership" in payment_form.cleaned_data:
                            if payment_form.cleaned_data['membership']!="":
                                fee=decimal.Decimal(payment_form.cleaned_data['membership'])

                                comment = ""

                                if "membership_receipt" in payment_form.cleaned_data:
                                    comment +="Membership Receipt #: " + payment_form.cleaned_data["membership_receipt"]+" "

                                if "borrow_fee_adjust_justification" in payment_form.cleaned_data:
                                    if payment_form.cleaned_data['membership_adjust_justification']!="":
                                        comment += payment_form.cleaned_data['membership_adjust_justification']
                                        adjustment_found=True

                                if fee!=0 or comment is not None:
                                    transaction=Transaction()
                                    transaction.create_transaction_record(request.user,member,Transaction.MEMBERSHIP_FEE,fee,comment)

                                    member.update_membership_date()



                        #toy bond transaction
                        if "loan_bond" in payment_form.cleaned_data:
                            if payment_form.cleaned_data['loan_bond']!="":
                                fee=decimal.Decimal(payment_form.cleaned_data['loan_bond'])

                                if "loan_bond_adjust_justification" in payment_form.cleaned_data:
                                    if payment_form.cleaned_data['loan_bond_adjust_justification']!="":
                                        comment=payment_form.cleaned_data['loan_bond_adjust_justification']
                                        adjustment_found=True
                                    else:
                                        comment=None

                                if fee!=0 or comment is not None:
                                    transaction=Transaction()
                                    transaction.create_transaction_record(request.user,member,Transaction.LOAN_BOND,fee,comment)


                        if "loan_bond_refund" in payment_form.cleaned_data:
                             if payment_form.cleaned_data['loan_bond_refund']!="":
                                    fee=decimal.Decimal(payment_form.cleaned_data['loan_bond_refund'])
                                    if fee!=0:
                                        transaction=Transaction()
                                        comment=None
                                        transaction.create_transaction_record(request.user,member,Transaction.LOAN_BOND_REFUND,fee,comment)

                                    fees_records=Transaction.objects.filter(complete=False, member__id=member_id, transaction_type=Transaction.LOAN_BOND_REFUND)
                                    for item in fees_records:
                                        item.amount=fee
                                        item.comment=comment
                                        item.complete=True
                                        item.complete_date=thisDateTime().now()
                                        item.save()


                        #Member bond fee transaction
                        if "member_bond" in payment_form.cleaned_data:
                            if payment_form.cleaned_data['member_bond']!="":
                                fee=decimal.Decimal(payment_form.cleaned_data['member_bond'])
                                comment = None

                                if "member_bond_receipt" in payment_form.cleaned_data:
                                    member.bond_receipt_reference = payment_form.cleaned_data["member_bond_receipt"]
                                    comment = "Bond Receipt #: "+payment_form.cleaned_data["member_bond_receipt"]
                                else:
                                    print "ERROR"

                                if "member_bond_adjust_justification" in payment_form.cleaned_data:
                                    if payment_form.cleaned_data['member_bond_adjust_justification']!="":
                                        comment+=' '+payment_form.cleaned_data['member_bond_adjust_justification']
                                        adjustment_found=True

                                if fee!=0 or comment is not None:
                                    transaction=Transaction()
                                    transaction.create_transaction_record(request.user,member,Transaction.MEMBER_BOND,fee,comment)
                                    if fee==0 and comment is not None:
                                        member.bond_fee_paid=member.type.bond
                                    else:
                                        member.bond_fee_paid=fee
                                    member.save()


                        #overdue fee transaction completion
                        if "late_fee" in payment_form.cleaned_data:
                            if payment_form.cleaned_data['late_fee']!="":
                                fee=decimal.Decimal(payment_form.cleaned_data['late_fee'])

                                if "late_fee_adjust_justification" in payment_form.cleaned_data:
                                    if payment_form.cleaned_data['late_fee_adjust_justification']!="":
                                        comment=payment_form.cleaned_data['late_fee_adjust_justification']
                                        adjustment_found=True
                                    else:
                                        comment=None

                                if fee!=0 or comment is not None:
                                    fees_records=Transaction.objects.filter(complete=False, member__id=member_id, transaction_type=Transaction.LATE_FEE)

                                    for item in fees_records:
                                        item.amount=fee
                                        item.comment=comment
                                        item.complete=True
                                        item.complete_date = thisDateTime().now()
                                        item.save()

                        if "issue_fee" in payment_form.cleaned_data:
                            if payment_form.cleaned_data['issue_fee']!="":
                                fee=decimal.Decimal(payment_form.cleaned_data['issue_fee'])

                                if "issue_fee_adjust_justification" in payment_form.cleaned_data:
                                    if payment_form.cleaned_data['issue_fee_adjust_justification']!="":
                                        comment=payment_form.cleaned_data['issue_fee_adjust_justification']
                                        adjustment_found=True
                                    else:
                                        comment=None

                                if fee!=0 or comment is not None:
                                    fees_records=Transaction.objects.filter(complete=False, member__id=member_id, transaction_type=Transaction.ISSUE_FEE)

                                    for item in fees_records:
                                        item.amount=fee
                                        item.comment=comment
                                        item.complete=True
                                        item.complete_date = thisDateTime().now()
                                        item.save()

                        if "change" in payment_form.cleaned_data:
                            if payment_form.cleaned_data['change']!="":
                                change=decimal.Decimal(payment_form.cleaned_data['change'])

                        if "payment" in payment_form.cleaned_data:
                            if payment_form.cleaned_data['payment']!="":
                                fee=decimal.Decimal(payment_form.cleaned_data['payment'])
                                fee_paid=fee
                                if fee!=0 or adjustment_found:
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


                        context.update({"clear_form":True,"success":True})
                        #context.update({"success":True})



                        if "total_fee" in payment_form.cleaned_data:
                            if payment_form.cleaned_data['total_fee']!="":
                                fee_due = decimal.Decimal(payment_form.cleaned_data['total_fee'])

                        #look at submit actions

                        #TODO need to get total fees before changed to total to pay.
                        for item in request.POST:

                            if item=="add_credit":

                                if change>0: #add credit
                                    member.balance = member.balance - fee_due + fee_paid
                                    #print(member.balance)
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

                            # elif item=="return":
                            elif item=="paid":
                                transaction=Transaction()
                                transaction.create_transaction_record(request.user,member,Transaction.CHANGE,fee_paid-fee_due,balance_change=fee_due)
                                break

                            # elif item=="exact":
                            #     transaction=Transaction()
                            #     transaction.create_transaction_record(request.user,member,Transaction.CHANGE,0,balance_change=fee_due)
                            #     break




    default_loan_duration = get_config("default_loan_duration")

    #fill in other fees

    #TODO toy deposit
    balance=0
    late_fee=0
    issue_fee=0
    membership_fee=0
    member_bond=0
    loan_bond_refund=0
    borrow_date=thisDateTime().date()


    if member and not "clear_form" in context:
        balance=member.balance
        late_fees_records=Transaction.objects.filter(complete=False, member__id=member_id, transaction_type=Transaction.LATE_FEE)
        late_fee=sum(f.amount for f in late_fees_records)

        issue_fees_records=Transaction.objects.filter(complete=False, member__id=member_id, transaction_type=Transaction.ISSUE_FEE)
        issue_fee=sum(f.amount for f in issue_fees_records)

        loan_bond_refund_records=Transaction.objects.filter(complete=False, member__id=member_id, transaction_type=Transaction.LOAN_BOND_REFUND)
        loan_bond_refund=sum(f.amount for f in loan_bond_refund_records)

        if not member.membership_valid():
            membership_fee=member.type.fee

        if not member.bond_paid():
            member_bond=member.type.bond

    # new_borrow_list=TempBorrowList.objects.filter(member__id=member_id)




    payment_initial={'loan_duration':default_loan_duration, 'late_fee':late_fee, 'membership':membership_fee, 'issue_fee':issue_fee, 'member_bond':member_bond, 'credit':balance,'loan_bond_refund':loan_bond_refund,'borrow_date':borrow_date}

    if volunteer:
        context.update({"volunteering": "true"})
        payment_initial.update({"volunteering": "true"})

    if not payment_form or (payment_form and payment_form.is_valid()):
        payment_form = PaymentForm(temp_toy_list=new_borrow_list,initial=payment_initial)#, check_fields=True)




    #make borrow toys query result into a list of toys
    new_borrow_toy_list=[]
    for item in new_borrow_list:
        new_borrow_toy_list.append(item.toy)

    context.update({'payment_form': payment_form,"new_borrow_toy_list": new_borrow_toy_list})
    # context.update({"toy_details_form_new": handle_toy_details_form(request, new_borrow_toy_list)})
    context.update({"toy_details_form": handle_toy_details_form(request, new_borrow_toy_list, member_id)})

    return context



class PaymentForm(forms.Form):


    def __init__(self, *args, **kwargs):
        toyList=kwargs.pop("temp_toy_list", 0)


        super(PaymentForm, self).__init__(*args, **kwargs)

        if toyList:
            for toy in toyList:
                self.fields['repair_checkbox_%s' % toy.toy.id]=forms.BooleanField(required=False)
                self.fields['repair_checkbox_%s' % toy.toy.id].widget.attrs.update({'nolist':'True'})

        if "initial" in kwargs:
            if "volunteering" in kwargs["initial"]:
                self.fields['borrow_fee'].widget.attrs.update({"message":"Volunteering today - Borrow fees will be ignored"})
                self.fields['borrow_fee'].widget.attrs.pop("total_me",0)
                self.fields['borrow_fee'].widget.attrs.pop("adjust_button", 0)
                self.fields['borrow_fee_adjust_justification'].widget.attrs.update({"rawValue":"VOLUNTEER"})

            # if "check_fields" in kwargs:
            if "member_bond" in kwargs["initial"] and kwargs["initial"]["member_bond"]==0:
                del self.fields["member_bond"]
                del self.fields["member_bond_adjust_justification"]
                del self.fields["member_bond_receipt"]

            if "late_fee" in kwargs["initial"] and kwargs["initial"]["late_fee"]==0:
                del self.fields["late_fee"]
                del self.fields["late_fee_adjust_justification"]

            if "membership" in kwargs["initial"] and kwargs["initial"]["membership"]==0:
                del self.fields["membership"]
                del self.fields["membership_adjust_justification"]
                del self.fields["membership_receipt"]

            if "issue_fee" in kwargs["initial"] and kwargs["initial"]["issue_fee"]==0:
                del self.fields["issue_fee"]
                del self.fields["issue_fee_adjust_justification"]
        else:
            if len(args)>0:
                for field in self.fields:
                    if not field in args[0]:
                            del self.fields[field]


    numeric = RegexValidator(r'^[0-9.-]*$', 'Only numeric characters are allowed.')


    loan_durations = str(get_config("loan_durations"))
    loan_bond_enable= get_config("loan_bond_enable")
    credit_enable=get_config("credit_enable")
    minimum_member_bond=get_config("minimum_member_bond")

    loan_choices = []
    # so choices can be easily stored in settings
    for c in loan_durations:
        loan_choices.append((c, c))

     # fill in default loan duration




    #ensure any input with adjust button also has a justification field with suffix of _adjust_justification with its name

    borrow_date = forms.DateField(label="Borrow Date", input_formats=['%d/%m/%Y','%d/%m/%y'], widget=forms.DateInput(format='%d/%m/%y',attrs={'readonly':'readonly','title':'Date the toy(s) has been borrowed, defaults to today','nolist':'True'}))

    loan_duration = forms.ChoiceField(label="Loan duration in weeks",choices=loan_choices, widget=forms.RadioSelect(attrs={'nolist':'True'}))

    borrow_fee = forms.CharField(label="Borrow Fee $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'total_me':'positive','readonly':'readonly', 'adjust_button':'True',}))
    borrow_fee_adjust_justification = forms.CharField(required=False, max_length=100,widget=forms.HiddenInput(attrs={'type':'hidden'}))


    #works but needs a server restart
    if loan_bond_enable=='true':
        loan_bond = forms.CharField(required=False, label="Loan Bond $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'total_me':'positive','readonly':'readonly', 'adjust_button':'True',}))
        loan_bond_adjust_justification = forms.CharField(required=False, max_length=100,widget=forms.HiddenInput(attrs={'type':'hidden'}))

        loan_bond_refund = forms.CharField(required=False, label="Loan Bond Refund $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'total_me':'negative','readonly':'readonly'}))
        loan_bond_refund_adjust_justification = forms.CharField(required=False, max_length=100,widget=forms.HiddenInput(attrs={'type':'hidden'}))

    member_bond = forms.CharField(required=False, label="Member Bond $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'total_me':'positive','readonly':'readonly', 'adjust_button':'True', 'minimum_value':minimum_member_bond}))
    member_bond_adjust_justification = forms.CharField(required=False, max_length=100,widget=forms.HiddenInput(attrs={'type':'hidden'}))
    member_bond_receipt = forms.CharField(required=True, label="Member Bond Receipt", max_length=20,widget=forms.TextInput(attrs={}))

    late_fee = forms.CharField(required=False, label="Late Fee $", max_length=20, validators=[numeric], widget=forms.TextInput(attrs={'total_me':'positive','readonly':'readonly','adjust_button':'True'}))
    late_fee_adjust_justification = forms.CharField(required=False, max_length=100,widget=forms.HiddenInput(attrs={'type':'hidden'}))


    membership = forms.CharField(required=False, label="Membership $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'total_me':'positive','readonly':'readonly', 'adjust_button':'True'}))
    membership_adjust_justification = forms.CharField(required=False, max_length=100,widget=forms.HiddenInput(attrs={'type':'hidden'}))
    membership_receipt = forms.CharField(required=True, label="Membership Receipt", max_length=20,widget=forms.TextInput(attrs={}))

    #TODO enable donation
    # donation = forms.CharField(required=False, label="Donation", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'total_me':'positive',}))

    issue_fee = forms.CharField(required=False, label="Issue Fee $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'total_me':'positive','readonly':'readonly','adjust_button':'True'}))
    issue_fee_adjust_justification = forms.CharField(required=False, max_length=100,widget=forms.HiddenInput(attrs={'type':'hidden'}))

    total_fee = forms.CharField(label="Total Fee $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'hr':'True','readonly':'readonly'}))

    if credit_enable=='true':
        credit = forms.CharField(label="Credit Remaining $", max_length=50, widget=forms.TextInput(attrs={'readonly':'readonly'}))
        total_to_pay = forms.CharField(label="Total to Pay $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'readonly':'readonly'}))

    payment = forms.CharField(label="Payment $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'hr':'True', 'change_buttons':'True','title':'Enter the amount the member has paid'}))
    change = forms.CharField(label="Change $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'readonly':'readonly', 'cancel_button':'True'}))


    # def clean(self):
    #     cleaned_data = super(PaymentForm, self).clean()
    #     for field in self:
    #         print field.html_name
    #         print field.field.widget.attrs
    #         print field.field.required
    #         print
    #
    #     return cleaned_data