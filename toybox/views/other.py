from django.shortcuts import render
from django.core.urlresolvers import reverse
from shared import *

def home(request):
    return render(request, 'toybox/landing_page.html', {})

#########################
# Unimplemented workflows
def returns(request, member_id=None):

    # context = get_memsearch_context(request)

    context= handle_returns(request,member_id)

    print(context)

    #base page context
    context.update({"daily_balance":23.20,"login_name":"Jess Benning"})

    #page context
    # context.update({"member":{"name":"John Smith","status":True,"balance":12.50}})

    context.update({"issue_list":
                        ({"name":"None","value":0},
                        {"name":"Broken repairable","value":1},
                        {"name":"Broken not repairable","value":2},
                        {"name":"Minor missing piece","value":3},
                        {"name":"Major missing piece","value":4},
                        {"name":"Whole toy missing","value":5})})

    context.update({"toys":
                    ({"ID":"BT3", "name":"Big toy 3", "due_in":32, "issue":0, "fee":0},
                     {"ID":"BT2", "name":"Big toy 2","due_in":-3, "issue":0, "fee":2.5},
                     {"ID":"BT1", "name":"Big toy 1","due_in":52, "issue":0, "fee":0.5})})

    context.update(handle_member_search(request))

    return render(request, 'toybox/returns.html', context)

def membership_admin(request, member_id=None):
   # context = get_memsearch_context(request)
    context=handle_member_details(request, member_id)
    return render(request, 'toybox/membership_admin.html', context)



def transactions(request):
     return render(request, 'toybox/transactions.html')

def reports(request):
     return render(request, 'toybox/reports.html')
