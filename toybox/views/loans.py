from django.shortcuts import render
from shared import *

def loans(request, member_id=0):
    if (request.method == "GET"):
        form = MemberSearchForm(request.GET)
    context = get_memsearch_context(request)
    if member_id != 0:
        context.update(get_memsummary_context(member_id))
    return render(request, 'toybox/loans.html', context)

def member_loan(request, member_id):
    return render(request, 'toybox/member_loan.html', { 'member_id': member_id })
