from django.shortcuts import render
from shared import *

def handle_returns(request,member_id):
    context={}

    context.update(handle_member_search(request))

    if (request.method == "GET"):
        if (member_id):
            context.update(handle_member_summary(request, member_id))

    return context


def returns(request, member_id=None):

    context= handle_returns(request,member_id)

    # TODO get this from authentication and transaction register
    #base page context
    context.update({"daily_balance":23.20,"login_name":"Jess Benning"})


    # TODO get this from DB
    context.update({"issue_list":
                        ({"name":"None","value":0},
                        {"name":"Broken repairable","value":1},
                        {"name":"Broken not repairable","value":2},
                        {"name":"Minor missing piece","value":3},
                        {"name":"Major missing piece","value":4},
                        {"name":"Whole toy missing","value":5})})

    # TODO get this from DB borrowed list
    context.update({"toy_list":
                    ({"ID":"BT3", "name":"Big toy 3", "due_in":32, "issue":0, "fee":0},
                     {"ID":"BT2", "name":"Big toy 2","due_in":-3, "issue":0, "fee":2.5},
                     {"ID":"BT1", "name":"Big toy 1","due_in":52, "issue":0, "fee":0.5})})

    context.update(handle_member_search(request))

    return render(request, 'toybox/returns.html', context)
