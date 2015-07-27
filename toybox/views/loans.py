from django.shortcuts import render
from shared import *


def loans(request, member_id):
    context = handle_member_search(request)

    # Always need this so search box renders
    context.update(handle_toy_search(request))

    # Only need to handle these frames if member_id set
    if (member_id):
        context.update(handle_member_summary(request, member_id))
        context.update(handle_borrowed_toy_list(request, member_id))

    # Only need to handle this frame is a toy is selected
    if (request.GET.get('tc')):
        context.update(handle_toy_summary(request))

    return render(request, 'toybox/loans.html', context)
