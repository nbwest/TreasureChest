from shared import *
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import ast


@login_required()
def shifts(request):

    rendered = render_ajax_request(request)
    if rendered != None:
        return rendered

    context = {"title":"Shifts"}
    context.update(base_data(request))

    context.update(handlePOST(context,request))

    GETresult=handleGET(request)
    if GETresult:
        return GETresult

    return render(request, 'toybox/shifts.html',context )

def handlePOST(context,request):
    return context

def handleGET(request):

    if (request.method == "GET" and request.GET):



        if "sort" in request.GET:
            # all_shifts = Shift.objects.all()

            all_shifts = Shift.objects.all().order_by("shift_date").distinct().values_list("shift_date", flat=True)

            col_filters = request.GET.get('filter',None)

            member_names=dict(Member.objects.all().order_by("id").values_list("id","name"))

            if col_filters:
                col_filters = ast.literal_eval(col_filters)
                filter_by_date('shift_date', col_filters)
                filter_by_general('volunteer_id', 'volunteer__name__icontains', col_filters)


            total,query = sort_slice_to_rows(request, all_shifts, col_filters, Shift)
            rows = list(query.values())


            newRows=[]
            vols=""
            if rows:
                last_date=rows[0]['shift_date']

                for row in rows:

                    if last_date != row['shift_date']:
                        newRows.append({"shift_date": last_date.strftime('%d/%m/%y'), "volunteer_id": vols})
                        last_date = row['shift_date']
                        vols=""

                    link = '<button title = "Member details" type = "button" class ="btn btn-link" onclick="getMemberSummary(this);" value="{0}" >{1}</button>'
                    link = link.format(row["volunteer_id"], member_names[row["volunteer_id"]])
                    vols += link + "  "

                if vols:
                    newRows.append({"shift_date": last_date.strftime('%d/%m/%y'), "volunteer_id": vols})

            context={"total":total,"rows":newRows}

            return JsonResponse(context)
    else:
        return None

