from django.shortcuts import render
from shared import *


def loans(request, member_id=0):
    if (request.method == "POST"):
        form = MemberSearchForm(request.POST)
        if form.is_valid():
            possible_members = fragment_search(form.cleaned_data['member_name_fragment'])
    else:
        form = MemberSearchForm()
        possible_members = None

    context = {'form': form,
               'members': possible_members}
    # if member_id != 0:
    #     context.update(get_memsummary_context(member_id))
    return render(request, 'toybox/loans.html', context)


def member_loan(request, member_id):
    return render(request, 'toybox/member_loan.html', {'member_id': member_id})
