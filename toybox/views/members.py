
from django.db.models import Count
from shared import *
from django.contrib.auth.decorators import login_required
import member_edit
import json


# POST - Guide: Use POST all the time except when you want the ability to bookmark a page, then use GET
#               Don't use GET to define actions
# GET
# /toybox/membership/ - display all members, clear form, submit button is "Add"
# /toybox/membership/1 - display all members, display member in form, submit button is "Update"
# /toybox/membership/?search=name_fragment - display search members, submit button is "Update"
# /toybox/membership/1/?search=name_fragment - display search members, submit button is "Update"






@login_required
def members(request, member_id=None):
    context = {"title": "Members"}

    rendered=render_ajax_request(request)
    if rendered != None:
        return rendered


    rendered=member_edit.render_ajax_request(request)
    if rendered != None:
        return rendered

    if request.method=="POST" and request.is_ajax():
        context.update(member_edit.handle_member_edit(request,member_id))
        rendered = render_to_string('toybox/member_edit.html', context)
        context.update({"member_edit_form":rendered})
        return HttpResponse(json.dumps(context))

    context.update(base_data(request))

    context.update({"members":Member.objects.filter(active=True).order_by('name')})

     # if no members have been searched for display all members
    if context["members"] != None:

        # get number of loans for each member
        overdue = Toy.objects.filter(
            due_date__lt=thisDateTime().date())  # .annotate(dcount=Count('member_loaned'))
        loans_overdue = {}
        for toy_due in overdue:
            if toy_due.member_loaned_id in loans_overdue:
                loans_overdue[toy_due.member_loaned_id] += 1
            else:
                loans_overdue.update({toy_due.member_loaned_id: 1})

        # probably a better way to do this, inserting into dict. better to have it attached to members in member list
        loans = Toy.objects.values('member_loaned').annotate(dcount=Count('member_loaned'))
        loan_counts = {}
        for loan in loans:
            if loan['dcount'] != 0:
                loan_counts.update({loan['member_loaned']: loan['dcount']})

        # print(loans_overdue)
        # print(loan_counts)

        context.update({"loan_counts": loan_counts, "loans_overdue": loans_overdue})

    # context.update(handle_member_edit(request, member_id))
    return render(request, 'toybox/members.html', context)


# def get_all_members_ordered_by_name():
#     # members=Member.objects.all().order_by('name')
#     members = Member.objects.filter(active=True).order_by('name')
#     return members

# def handle_member_toy_history(request, member_id):
#
#     return ToyHistory.objects.filter(member__id=member_id).order_by('date_time').select_related('toy')
#

# Form




