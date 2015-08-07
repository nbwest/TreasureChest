from django.shortcuts import render
from shared import *

def home(request):
    return render(request, 'toybox/landing_page.html', {})

#########################
# Unimplemented workflows
def returns(request):
    #context = get_memsearch_context(request)

    #base page context
    context = {"daily_balance":23.20, "current_page":"return", "member_name":"Jess Benning"}

    #page context
    context.update({"member_status":True,"member_balance":12.50})

    context.update({"issue_list":
                        ({"name":"None","value":0},
                        {"name":"Broken repairable","value":1},
                        {"name":"Broken not repairable","value":2},
                        {"name":"Minor missing piece","value":3},
                        {"name":"Major missing piece","value":4},
                        {"name":"Whole toy missing","value":5})})

    context.update({"borrowed_toys":
                    ({"ID":"BT3", "name":"Big toy 3", "due_in":32, "issue":0},
                     {"ID":"BT2", "name":"Big toy 2","due_in":23, "issue":0},
                     {"ID":"BT1", "name":"Big toy 1","due_in":52, "issue":0})})



    return render(request, 'toybox/returns.html', context)

def membership_admin(request):
   # context = get_memsearch_context(request)
    return render(request, 'toybox/membership_admin.html')#, context)

def end_of_day(request):
    return render(request, 'toybox/end_of_day.html')
