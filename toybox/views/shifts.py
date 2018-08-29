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
    context.update(handle_shift(request))

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


def handle_shift(request):
    context = {}

    if request.method == "POST":


        if "selected_list" in request.POST:
            selected_ids = request.POST["selected_list"].split(" ")
            Shift.objects.filter(shift_date=thisDateTime().date()).delete()
            if len(selected_ids) >= 1:
                if selected_ids[0] != "":
                    selected_ids = list(map(int, selected_ids))

                        #clear current list ing db and add new ones from dialog.

                    for id in selected_ids:
                        new_volunteer = Member.objects.get(pk=id)
                        if new_volunteer:
                            shift = Shift(volunteer=new_volunteer, shift_date=thisDateTime().date())
                            shift.save()

                        else:
                            context.update({"error": "volunteer not selected"})




        # if "remove_vol" in request.POST:
        #
        #
        #     # for id in ids:
        #     Shift.objects.get(shift_date=thisDateTime().date(), volunteer=id).delete()
        #
        #     context.update({"setting_shift": "true"})

        # elif "add_vol" in request.POST:
        #     # add volunteer
        #     context.update({"setting_shift": "true"})
        #     new_volunteer_id = int(request.POST["add_vol"])
        #     new_volunteer = Member.objects.get(pk=new_volunteer_id)
        #     if new_volunteer:
        #         in_shift = Shift.objects.filter(shift_date=thisDateTime().date(), volunteer=new_volunteer)
        #
        #         if in_shift.count() == 0:
        #             shift = Shift(volunteer=new_volunteer, shift_date=thisDateTime().date())
        #             shift.save()
        #         else:
        #             context.update({"error": "volunteer already added"})
        #     else:
        #         context.update({"error": "volunteer not selected"})
#error wrong when nothing entered
#volunteer already added coming up whe it shouldn't
#filter out ones in shift already???
            #can it be made without refreshing the page?
    todays_shift = Shift.objects.filter(shift_date=thisDateTime().date()).select_related('volunteer')

    if todays_shift.count() == 0:
        todays_shift = None

    members_list = Member.objects.all().values_list("id", "name", "partner")

    context.update({"shift": todays_shift, "members": members_list})

    return context