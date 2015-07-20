from django.shortcuts import render
from shared import *


def loans(request, member_id=0):
    context = handle_member_search(member_id, request)
    context.update(handle_borrowed_toy_list(member_id))
    return render(request, 'toybox/loans.html', context)
