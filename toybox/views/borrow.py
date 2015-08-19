from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from shared import *
from django.db.models import *
from datetime import *

def borrow(request, member_id):

    context={}
    # If borrow button has been pushed, handle borrow of toy and reload page

    # Only need to handle this frame is a toy is selected
    toy_code = request.GET.get('tc')
    if (toy_code):
        context.update(handle_toy_summary(request))
    # toy_code = request.GET.get('bt')
    # if (toy_code):
        toy = get_object_or_404(Toy, code=toy_code)
        member = get_object_or_404(Member, pk=member_id)
        print "Loaning toy"
        # TODO include borrow duration, 1 is placeholder
        toy.borrow(member,1)

        # return HttpResponseRedirect(reverse('toybox:borrow', kwargs={'member_id': member_id}) )

    context.update( handle_member_search(request))

    # Always need this so search box renders
    context.update(handle_toy_search(request))

    # Only need to handle these frames if member_id set
    if (member_id):
        context.update(handle_member_summary(request, member_id))
        context.update(handle_borrowed_toy_list(request, member_id))

    # TODO retrieve from elsewhere
    #base page context
    context.update({"daily_balance":23.20, "login_name":"Jess Benning"})

    return render(request, 'toybox/borrow.html', context)


def handle_borrowed_toy_list(request, member_id):
    context = {}
    if (member_id):
        # toys = Toy.objects.all().annotate(due_in=F("due_date")-timezone.now()).filter(member_loaned=member_id)
        #toys= Toy.objects.all().extra(select={"difference":"due_date"-timezone.now()}).filter(member_loaned=member_id)
        toys = Toy.objects.filter(member_loaned=member_id).values()


#TODO time/date is wrong here - research timezone stuff
    if (toys):
        for t in toys:
            print( timezone.now(), t["due_date"])
            t.update({"due_in":(t["due_date"]-timezone.now().date()).days})


    context = {'toy_list': toys}

    return context