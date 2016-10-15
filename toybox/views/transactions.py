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


def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

@login_required()
def transactions(request):

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
                    try:
                        setTill(form.cleaned_data['new_till_value'], till, request)
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


def handleTotalsForm(request):
    context = {}
    form=None
    if request.method == "POST" and "totals_date_submit" in request.POST:
        form = TransactionTotalsForm(request.POST)
        if form.is_valid():
            if "query_date" in request.POST:

                d = datetime.datetime.strptime(request.POST["query_date"], "%d/%m/%Y").date()
                tr=Transaction.objects.filter(date_time__startswith=d)

                results={}
                if tr.count()!=0:
                    till_end=tr.last().balance
                    till_start=tr.first().balance

                    context.update({"total_takings":till_end-till_start})
                    context.update({"till_start": till_start})
                    context.update({"till_end": till_end})



                    for choice in Transaction.TRANSACTION_TYPE_CHOICES:

                       if choice[0] not in [Transaction.CHANGE,Transaction.PAYMENT]:
                           total=tr.filter(transaction_type=choice[0]).aggregate(Sum('amount'))["amount__sum"]
                           if total:
                               results.update({choice[1]:total})

                context.update({"totals":results, "query_date":d})

        context.update({"totals_form":form})
    else:
        context.update({"totals_form": TransactionTotalsForm()})



    return context



def handleGET(request):

    if (request.method == "GET" and request.GET):

        if "filter_data" in request.GET:

            if "transaction_type" in request.GET["filter_data"]:

                listed_unique_values=Transaction.objects.all().values_list("transaction_type", flat=True).distinct()

                result={}
                for element in listed_unique_values:
                    result.update({Transaction.TRANSACTION_TYPE_CHOICES[element][1]:Transaction.TRANSACTION_TYPE_CHOICES[element][1]})

                return JsonResponse(result)

            if "complete" in request.GET["filter_data"]:
                listed_unique_values = Transaction.objects.all().values_list("complete", flat=True).distinct()

                result = {}
                for element in listed_unique_values:
                    result.update({str(element):str(element)})

                return JsonResponse(result)

        if "sort" in request.GET:

            #data select need to show all possibilities, not just those in the current page

            all_transactions = Transaction.objects.all()
            total = all_transactions.count()

            sort = request.GET.get('sort', 'id')
            order = request.GET.get('order', 'asc')
            limit = int(request.GET.get('limit',total))
            offset = int(request.GET.get('offset',0))
            col_filters = request.GET.get('filter',None)


            if order=="desc":
                dir="-"
            else:
                dir=""


            toy_historys=ToyHistory.objects.all().order_by("transaction").exclude(transaction__isnull=True).values("toy","toy__code","toy__name","transaction")
            member_names=dict(Member.objects.all().order_by("id").values_list("id","name"))


            if col_filters:
                col_filters=ast.literal_eval(col_filters)
                if "transaction_type" in col_filters:
                    for choice in Transaction.TRANSACTION_TYPE_CHOICES:
                        if col_filters["transaction_type"]==choice[1]:
                            col_filters.update({"transaction_type":choice[0]})



                if "member_id" in col_filters:
                     col_filters.update({"member__name__icontains":col_filters["member_id"]})
                     col_filters.pop("member_id")

                if "volunteer_reporting" in col_filters:
                     col_filters.update({"volunteer_reporting__icontains":col_filters["volunteer_reporting"]})
                     col_filters.pop("volunteer_reporting")

                if "comment" in col_filters:
                     col_filters.update({"comment__icontains":col_filters["comment"]})
                     col_filters.pop("comment")

                if "date_time" in col_filters:
                    dt=datetime.datetime.strptime( col_filters["date_time"], "%d/%m/%y")# %H:%M" )
                    col_filters.update({"date_time__startswith":dt.date})
                    col_filters.pop("date_time")

                if "id" in col_filters:
                    col_filters.update({"id__contains":col_filters["id"]})
                    col_filters.pop("id")

                if "complete" in col_filters:
                    col_filters.update({"complete":str2bool(col_filters["complete"])})

                total=all_transactions.filter(**col_filters).count()
                transactions=all_transactions.filter(**col_filters).order_by(dir + sort)[offset:offset + limit]
            else:
                transactions=all_transactions.order_by(dir+sort)[offset:offset+limit]

            rows=list(transactions.values())

            for row in rows:

                row["transaction_type"]=Transaction.TRANSACTION_TYPE_CHOICES[row["transaction_type"]][1]

                if row["member_id"]:
                    row["member_id"]=member_names[row["member_id"]]

                row["date_time"]=row["date_time"].strftime('%d/%m/%y %H:%M')

                row["complete"]=str(row["complete"])

                matching=filter(lambda th: th['transaction'] == row["id"], toy_historys)
                if matching:
                    toys=""

                    for toy in matching:
                        toy_url=reverse("toybox:toys",kwargs={'toy_id':toy["toy"]})
                        toys+="<a href=\""+toy_url+"\">"+toy["toy__code"]+", "+toy["toy__name"]+"</a> <br>"

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




def setTill(till_value, daily_balance, request):


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

    transaction.create_transaction_record(request.user,None,type,adj,comment="TILL ADJ",balance_change=adj)





class TransactionActionForm(forms.Form):

    balance=0.0

    def __init__(self, *args, **kwargs):
            self.balance=kwargs.pop("daily_balance", 0)
            super(TransactionActionForm, self).__init__(*args, **kwargs)
            numeric = RegexValidator(r'^[0-9.-]*$', 'Only numeric characters are allowed.')

            self.fields['bank_value']= forms.CharField(required=False, label="Remove from Till $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={'button_bank_amount':'Bank Amount','button_bank_all':'Bank '+'${:,.2f}'.format(self.balance) }))
            self.fields['new_till_value']= forms.CharField(required=False, label="New Till value $", max_length=20, validators=[numeric],widget=forms.TextInput(attrs={ 'button_set_till':'Set Till'}))


    new_till_value = forms.CharField()
    bank_value = forms.CharField()




class TransactionTotalsForm(forms.Form):
    query_date = forms.DateField(label="Date", input_formats=['%d/%m/%Y'], widget=forms.DateInput(format='%d/%m/%Y',attrs={'readonly':'readonly','title':'Date to display totals for'}))