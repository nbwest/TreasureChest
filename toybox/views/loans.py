from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from shared import *


def loans(request, member_id):
    # If borrow button has been pushed, handle borrow of toy and reload page
    toy_code = request.GET.get('bt')
    if (toy_code):
        toy = get_object_or_404(Toy, code=toy_code)
        member = get_object_or_404(Member, pk=member_id)
        print "Loaning toy"
        toy.borrow(member,1)
        return HttpResponseRedirect(reverse('toybox:member_loan', kwargs={'member_id': member_id}) )

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

    #base page context
    context.update({"daily_balance":23.20, "login_name":"Jess Benning"})

    #print(context)

    return render(request, 'toybox/loans.html', context)
