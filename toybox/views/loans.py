from django.shortcuts import render
from shared import *


def loans(request):
    context = handle_member_search(request)
    context.update(handle_borrowed_toy_list(request))
    context.update(handle_member_summary(request))
    context.update(handle_toy_search(request))
    return render(request, 'toybox/loans.html', context)
