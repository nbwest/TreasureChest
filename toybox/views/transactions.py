from django.shortcuts import render
from shared import *
from django import forms
from django.core.validators import *
import decimal
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import JsonResponse
import ast
from django.db.models import Sum

#import pytz




@login_required()
def transactions(request):
    rendered = render_ajax_request(request)
    if rendered != None:
        return rendered

    context = {"title":"Transactions"}
    context.update(base_data(request))

    context.update(handlePOST(context,request))

    GETresult=handleGET(request)
    if GETresult:
        return GETresult

    return render(request, 'toybox/transactions.html',context )

def handlePOST(context, request):

    user = User.objects.get(username=request.user.username)

    if user.has_perm("toybox.transaction_actions"):
         context.update(handleTransactionActionForm(request, context['daily_balance']))

    context.update(handleTotalsForm(request))

    return context


def handleTransactionActionForm(request, till):
    context={}
    form=None
    if (request.method == "POST"):
        form = TransactionActionForm(request.POST)
        if form.is_valid():

            if "button_set_till" in request.POST:
                if "new_till_value" in form.cleaned_data:
                    if "new_till_value_comment" in form.cleaned_data:
                        comment=form.cleaned_data["new_till_value_comment"]
                    else:
                        comment=None

                    try:
                        setTill(form.cleaned_data['new_till_value'], till, request,comment)
                    except ValueError as e:
                        form.add_error("new_till_value", e.message)

            if "button_bank_amount" in request.POST:
                if "bank_value" in form.cleaned_data:
                    try:
                        setBanking(form.cleaned_data['bank_value'], till, request)
                    except ValueError as e:
                        form.add_error("bank_value", e.message)

            if "button_bank_all" in request.POST:
                transaction = Transaction()
                transaction.create_transaction_record(request.user, None, Transaction.ADJUSTMENT_DEBIT,
                                                      -till, comment="BANK ALL TILL",
                                                      balance_change=-till)

            # call to update current balance after transactions
            context.update({"transaction_form": form})
            context.update(base_data(request))


    if not form or len(form.errors) == 0:
        context.update({"transaction_form": TransactionActionForm(daily_balance=till)})


    return context

# def date_string_to_utc(str_dt, fmt):
#     local = datetime.datetime.strptime(str_dt, fmt)
#     timezoneLocal = pytz.timezone(settings.TIME_ZONE)
#     local_dt = timezoneLocal.localize(local, is_dst=None)
#     utc_dt = local_dt.astimezone(pytz.utc)
#
#     return utc_dt

def handleTotalsForm(request):
    context = {}
    headings = []
    totals = list([0])
    results = []
    form=None
    if request.method == "POST" and "query_date" in request.POST and request.POST["query_date"]:
        form = TransactionTotalsForm(request.POST)
        if form.is_valid():
            # if "button_date_submit" in request.POST:

                d = form.cleaned_data['query_date']#'.datetime.strptime(request.POST["query_date"], "%d/%m/%Y").date()

                # utc_dt = date_string_to_utc(request.POST["query_date"], "%d/%m/%Y")

                tr=Transaction.objects.filter((Q(date_time__startswith=d)| Q(complete_date__startswith=d)), complete=True).select_related('member')

                if tr.count() != 0:

                    members = tr.values('member', 'member__name').distinct()
                    tr_types= tr.values('transaction_type').distinct()




                    headings.append("Name")

                    for tr_type in tr_types:
                        headings.append(Transaction.TRANSACTION_TYPE_CHOICES[tr_type["transaction_type"]][1])
                        totals.append(0)
                    headings.append("Total")



                    for member in members:
                        member_tr=tr.filter(member=member["member"])
                        member_fees=[]
                        member_fees.append(member["member__name"])

                        for tr_type in tr_types:
                            member_fees.append(member_tr.filter(transaction_type=tr_type["transaction_type"]).aggregate(Sum("amount"))["amount__sum"])

                        member_fees.append(member_tr.exclude(transaction_type=Transaction.PAYMENT).exclude(transaction_type=Transaction.CHANGE).aggregate(Sum("amount"))["amount__sum"])

                        for index,item in enumerate(totals):
                            if member_fees[index+1]:
                                totals[index]=Decimal(item)+Decimal(member_fees[index+1])

                        results.append(member_fees)

                    tr=tr.filter(date_time__startswith=d)
                    till_end=tr.latest("date_time").balance
                    till_start=tr.earliest("date_time").balance

                    context.update({"total_takings":till_end-till_start})
                    context.update({"till_start": till_start})
                    context.update({"till_end": till_end})

                #
                #
                #     for choice in Transaction.TRANSACTION_TYPE_CHOICES:
                #
                #        # if choice[0] not in [Transaction.CHANGE]:
                #            total=tr.filter(transaction_type=choice[0]).aggregate(Sum('amount'))["amount__sum"]
                #            if total:
                #                results.update({choice[1]:total})

                    context.update({"headings":headings,"totals":totals,"fees":results, "query_date":d})
                else:
                    form.add_error('query_date','No transactions found')

        context.update({"totals_form":form})
    else:
        context.update({"totals_form": TransactionTotalsForm()})



    return context



def handleGET(request):

    if (request.method == "GET" and request.GET):

        if "filter_data" in request.GET:

            result = get_filter_data_from_choices("transaction_type", request, Transaction.objects.all(), Transaction.TRANSACTION_TYPE_CHOICES)
            if result:
                return JsonResponse(result)

            result = get_filter_data_direct("complete", request, {"True":"True","False":"False"})
            if result:
                return JsonResponse(result)


        if "sort" in request.GET:
            all_transactions = Transaction.objects.all()

            col_filters = request.GET.get('filter',None)

            toy_historys=ToyHistory.objects.all().order_by("transaction").exclude(transaction__isnull=True).values("toy","toy__code","toy__name","transaction")
            member_names=dict(Member.objects.all().order_by("id").values_list("id","name"))

            if col_filters:
                col_filters = ast.literal_eval(col_filters)
                filter_by_choice_lookup('transaction_type', Transaction.TRANSACTION_TYPE_CHOICES, col_filters)
                filter_by_general('member_id', 'member__name', col_filters)
                filter_by_contains('member__name', col_filters)
                filter_by_contains('volunteer_reporting', col_filters)
                filter_by_contains('comment', col_filters)
                filter_by_date('date_time', col_filters)
                filter_by_contains('id', col_filters)
                filter_by_choice_lookup('complete', ((False,'False'),(True,'True')), col_filters)

            total,query = sort_slice_to_rows(request, all_transactions, col_filters, Transaction)
            rows = list(query.values())


            for row in rows:

                format_by_choice_lookup("transaction_type", Transaction.TRANSACTION_TYPE_CHOICES, row)

                if row["member_id"]:
                    link = '<button title = "Member details" type = "button" class ="btn btn-link" onclick="getMemberSummary(this);" value="{0}" >{1}</button>'.format(
                        row["member_id"], member_names[row["member_id"]])
                    row["member_id"] = link

                format_by_date('date_time', row)

                row["complete"]=str(row["complete"])

                matching=filter(lambda th: th['transaction'] == row["id"], toy_historys)
                if matching:
                    toys=""
                    for toy in matching:
                        toys+= '<button title = "Toy details" type = "button" class ="btn btn-link" onclick="getToy(this);" value="{0}" >{1} {2}</button><br>'.format(
                            toy["toy"], toy["toy__code"], toy["toy__name"])
                        row.update({"toys":toys})


            context={"total":total,"rows":rows}

            return JsonResponse(context)
    else:
        return None

def checkAmount(till_value):
    if till_value=="":
        raise ValueError( "Value required")

    try:
        value=decimal.Decimal(till_value)
    except:
        raise ValueError("Value not a number")

    if value<0:
        raise ValueError("Negative numbers not accepted")

    if value>1000:
        raise ValueError("Value must be less than or equal to $1000")

    return value


def setBanking(till_value, daily_balance, request):

    try:
        value=checkAmount(till_value)
    except:
        raise

    if value>=0:
        if daily_balance-value>=0:

             transaction=Transaction()
             type=Transaction.ADJUSTMENT_DEBIT
             transaction.create_transaction_record(request.user,None,type,-value,comment="BANK TILL",balance_change=-value)
        else:
            raise ValueError("Invalid amount - Till less than zero")
    else:
       raise ValueError("Negative numbers not accepted")




def setTill(till_value, daily_balance, request,comment=""):


    try:
        value=checkAmount(till_value)
    except:
        raise

    try:
        current_till=decimal.Decimal(daily_balance)
    except:
        raise ValueError("Daily balance not a number")

    if current_till==value:
        raise ValueError("Value must be different to balance")

    transaction=Transaction()

    if value>current_till:
         type=Transaction.ADJUSTMENT_CREDIT
         adj=value-current_till
    else:
         type=Transaction.ADJUSTMENT_DEBIT
         adj=-(current_till-value)

    transaction.create_transaction_record(request.user,None,type,adj,comment="TILL ADJ "+comment,balance_change=adj)





class TransactionActionForm(forms.Form):

    balance=0.0

    def __init__(self, *args, **kwargs):
            self.balance=kwargs.pop("daily_balance", 0)
            super(TransactionActionForm, self).__init__(*args, **kwargs)
            numeric = RegexValidator(r'^[0-9.-]*$', 'Only numeric characters are allowed.')

            self.fields['bank_value']= forms.CharField(required=False, label="Remove from Till $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'hr':'true','button_bank_amount':'Bank Amount','button_bank_all':'Bank '+'${:,.2f}'.format(self.balance) }))
            self.fields['new_till_value']= forms.CharField(required=False, label="New Till value $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={ 'button_set_till':'Set Till'}))


    new_till_value = forms.CharField()
    new_till_value_comment = forms.CharField(required=False, label="New Till value comment", max_length=200)
    bank_value = forms.CharField()




class TransactionTotalsForm(forms.Form):
    query_date = forms.DateField(label="Date", input_formats=['%d/%m/%Y','%d/%m/%y'], widget=forms.DateInput(format='%d/%m/%y',attrs={'button_date_submit':'Get totals','title':'Date to display totals for'}))