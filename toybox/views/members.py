
from django.db.models import Count
from shared import *
from django.contrib.auth.decorators import login_required
import member_edit
import json
import ast
from django.http import JsonResponse
from django.core.urlresolvers import reverse
from django.db.models import IntegerField,CharField, Case, Value, When
from django.db.models import F
from django.db.models import Prefetch


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

    GETresult = handleGET(request)
    if GETresult:
        return GETresult

    return render(request, 'toybox/members.html', context)



def handleGET(request):
    import time
    if (request.method == "GET" and request.GET):

        if "filter_data" in request.GET:

            result=get_filter_data_direct("status",request,{'Valid':'Valid','Due':'Due','Upcoming':'Upcoming'})
            if result:
                return JsonResponse(result)

            result = get_filter_data_direct("bond_status", request, {'Paid': 'Paid', 'Unpaid': 'Unpaid'})
            if result:
                return JsonResponse(result)


        col_filters = {}
        if "sort" in request.GET:
            col_filters = request.GET.get('filter',None)

            if col_filters:
                col_filters=ast.literal_eval(col_filters)
                BOOLEAN_CHOICE=((True, 'True'),(False,'False'))

                filter_by_contains('name',col_filters)
                filter_by_date('join_date', col_filters)
                filter_by_contains('phone_number1',col_filters)
                filter_by_contains('email_address',col_filters)
                filter_by_contains('membership_receipt_reference',col_filters)
                filter_by_choice_lookup('volunteer_capacity_wed', BOOLEAN_CHOICE, col_filters)
                filter_by_choice_lookup('volunteer_capacity_sat', BOOLEAN_CHOICE, col_filters)
                filter_by_choice_lookup('potential_volunteer', BOOLEAN_CHOICE, col_filters)
                filter_by_choice_lookup('volunteer', BOOLEAN_CHOICE, col_filters)
                filter_by_choice_lookup('committee_member', BOOLEAN_CHOICE, col_filters)
                filter_by_contains('comment', col_filters)

        from shared import get_config
        warning_duration = get_config("membership_warning_duration")
        warning_end_date=thisDateTime().date()+timedelta(days=warning_duration)



        valid_members = Member.objects.filter(active=True).annotate(
                loans=Count('toy')).annotate(
                loans_overdue=Count(Case(
                    When(toy__due_date__lt=thisDateTime().date(), then=1),
                    output_field=IntegerField()
                    ))
                ).annotate(
            status=Case(
                When(Q(membership_end_date__lte=warning_end_date) & Q(membership_end_date__gt=thisDateTime().date()),
                     then=Value("Upcoming")),
                When( membership_end_date__gt=thisDateTime().date(),then=Value("Valid")),
                default=Value("Due"),
                output_field=CharField()
            )).annotate(
                bond_status = Case(
                    When(Q(bond_fee_paid__gt=0), then=Value("Paid")),
                    default=Value("Unpaid"),
                    output_field=CharField()
        )
        )

        total, query = sort_slice_to_rows(request, valid_members, col_filters, Member)
        rows = list(query.values())

        tick = '<span class="glyphicon glyphicon-ok text-success"></span>'
        cross = '<span class="glyphicon glyphicon-remove text-danger"></span>'
        NA = '<span class="glyphicon glyphicon-ban-circle text-danger"></span>'

        toy_history = "<button title = 'Toy History' type = 'button' class ='btn btn-link' onclick='getMemberToyHistory(this);' value='{0}'><span class ='glyphicon glyphicon-time' aria-hidden='true'></span></button>"
        edit_icon = "<button title = 'Edit member details' type = 'button' class ='btn btn-link' onclick='getMemberDetails(this);' value='{0}'><span class ='glyphicon glyphicon-pencil' aria-hidden='true'></span></button>"
        loans="<a href='{0}'><span class='label {1} label-as-badge' title='{2}'>{3}</span></a>"
        status="<span class ='label {0} label-as-badge'>{1}</span>"

        for row in rows:

            if row["loans"]==0:
                title='No loans'
                badge="label-default"
            else:
                if row["loans_overdue"]:
                   title=str(row["loans_overdue"])+" overdue"
                   badge="label-danger"
                else:
                    title = 'Loans - click to go to returns'
                    badge = "label-success"

            link = reverse("toybox:returns", kwargs={'member_id': str(row["id"])})
            row["loans"] = loans.format(link,badge,title,str(row["loans"]))
            row["loans"] += toy_history.format(str(row["id"])) + edit_icon.format(str(row["id"]))

            if row["volunteer"]:
                if row["volunteer_capacity_wed"]:
                    row["volunteer_capacity_wed"] = tick
                else:
                    row["volunteer_capacity_wed"] = cross

                if row["volunteer_capacity_sat"]:
                    row["volunteer_capacity_sat"] = tick
                else:
                    row["volunteer_capacity_sat"] = cross


                row["potential_volunteer"] = NA
            else:
                row["volunteer_capacity_wed"] = NA
                row["volunteer_capacity_sat"] = NA
                if row["potential_volunteer"]:
                    row["potential_volunteer"] = tick
                else:
                    row["potential_volunteer"] = cross


            if row["committee_member"]:
                row["committee_member"] = tick
            else:
                row["committee_member"] = cross

            if row["volunteer"]:
                row["volunteer"] = tick
            else:
                row["volunteer"] = cross


            if row["status"]=="Upcoming":
                badge = "label-warning"
            elif  row["status"]=="Due":
                badge = "label-danger"
            else:
                badge = "label-success"

            row["status"]=status.format(badge,row["status"])



            if row["bond_status"]=="Paid":
                badge = "label-success"
            else:
                badge = "label-danger"
            row["bond_status"] = status.format(badge,row["bond_status"])


            format_by_date('join_date', row)
            format_by_date('membership_end_date', row)


        context={"total":total,"rows":rows}

        return JsonResponse(context)
    else:
        return None



