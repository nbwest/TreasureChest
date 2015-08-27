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



    context.update({"issue_list":IssueChoiceType.ISSUE_TYPE_CHOICES[:IssueChoiceType.RETURNED_MISSING_PIECE]})

    if (member_id):
        context.update(handle_member_summary(request, member_id))
        context.update(handle_borrowed_toy_list(request, member_id))


    # TODO get this from DB borrowed list
    # context.update({"toy_list":
    #                 ({"ID":"BT3", "name":"Big toy 3", "due_in":32, "issue":0, "fee":0},
    #                  {"ID":"BT2", "name":"Big toy 2","due_in":-3, "issue":0, "fee":2.5},
    #                  {"ID":"BT1", "name":"Big toy 1","due_in":52, "issue":0, "fee":0.5})})

    context.update(handle_member_search(request))

    return render(request, 'toybox/returns.html', context)

# class ReturnsForm(forms.Form):
#     type=ModelChoiceField(queryset=MemberType.objects.all(),label="Member Type")
#