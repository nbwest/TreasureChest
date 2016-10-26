from shared import *
from django.contrib.auth.decorators import login_required
from math import ceil
from django.shortcuts import *
import ast
from django.db.models import Sum
from django.core.urlresolvers import reverse
from django.http import JsonResponse

# Provide estimate of borrow cost based on purchase cost
# Calculates 1% of purchase cost rounded up to nearest $0.50
def estimate_borrow_cost(purchase_cost):
    onepc = float(purchase_cost)/100.0
    return 0.5 * ceil(2.0 * onepc)


@login_required()
def toys(request):


    rendered=render_ajax_request(request)
    if rendered != None:
        return rendered

    rendered=handleGET(request)
    if rendered != None:
        return rendered

    context = {"title":"Toys"}

    loan_bond_enable= get_config("loan_bond_enable")
    context.update({"loan_bond_enable":loan_bond_enable})

    context.update(base_data(request))
    context.update(handle_stocktake(request))

    # import time
    # start = time.time()
    rendered=render(request, 'toybox/toys.html', context)
    # end = time.time()
    # print("TOY QUERY: "+str(end - start))

    return rendered



def handle_stocktake(request):
    context={}

    if request.method=="POST":
        if "btn_stocktake_checked" or "btn_check" in request.POST:
            for key,value in request.POST.iteritems():

                if key=="stocktake" in request.POST:
                    selected=request.POST.getlist('stocktake')
                    for item in selected:
                      toy=Toy.objects.get(pk=int(item))

                      if "btn_stocktake_checked" in request.POST:
                         toy.last_stock_take=thisDateTime()

                      toy.last_check=thisDateTime()

                      if toy.state==Toy.ON_LOAN:
                         toy.state=Toy.AVAILABLE
                         toy.member_loaned=None

                      toy.save()

                elif key.startswith("issue_type"):

                    id=key.rpartition('_')[2]
                    toy=Toy.objects.get(pk=id)
                    toy.issue_type=int(value)
                    toy.state=toy.issue_type_to_state(toy.issue_type)
                    toy_history=ToyHistory()
                    toy_history.record_toy_event(toy,request.user,thisDateTime().now())
                    if "issue_comment_"+id in request.POST:
                        toy.issue_comment=request.POST["issue_comment_"+id]
                    toy.save()

                elif key.startswith("issue_comment"):
                    id=key.rpartition('_')[2]
                    if not "issue_type_"+id in request.POST:
                        toy=Toy.objects.get(pk=id)
                        toy.issue_comment=value
                        toy_history=ToyHistory()
                        toy_history.record_toy_event(toy,request.user,thisDateTime().now())
                        toy.save()

    return(context)

def filter_by_contains(field_name, filters):
    if field_name in filters:
        filters.update({field_name+"__icontains": filters[field_name]})
        filters.pop(field_name)

def filter_by_date(field_name,filters):
    if field_name in filters:
        dt = datetime.datetime.strptime(filters[field_name], "%d/%m/%y")
        filters.update({field_name+"__startswith": dt.date()})
        filters.pop(field_name)

def filter_by_general(field_name, query, filters):
    if field_name in filters:
        filters.update({query: filters[field_name]})
        filters.pop(field_name)

def filter_by_choice_lookup(field_name, choices, filters):
    if field_name in filters:
        for choice in choices:
            if filters[field_name]==choice[1]:
               filters.update({field_name:choice[0]})


def format_by_choice_lookup(field_name,choice,row):
    if field_name in row:
        row[field_name] = choice[row[field_name]][1]

def format_by_list_lookup(field_name, list, row):
    if row[field_name]:
        row[field_name] = list[row[field_name]]

def format_by_date(field_name,row):
    if row[field_name]:
         row[field_name] = row[field_name].strftime('%d/%m/%y')

def format_by_control(field_name,form,row):

    if field_name in row:
        render = form.fields["%s_%s" % (field_name,row["id"])].widget.render("%s_%s" % (field_name,row["id"]),row[field_name], {"class": "form-control"})
        row['%s_edit' % field_name] = render

def format_by_image(field_name,list,row):
    if row[field_name]:
        row[field_name] = '<a href = "{0}{1}" ><img class ="img-thumbnail"  style="image-orientation:from-image; " src="{0}{1}" ></a>'.format(settings.MEDIA_URL, list[row[field_name]])

# def format_by_link(field_name,link,row):
#     if row[field_name]:
#         link = link.format(row[field_name])
#         row[field_name] = link


def get_filter_data_from_choices(field_name,request,source_query,choice):
    result = {}
    if field_name in request.GET["filter_data"]:
        listed_unique_values = source_query.values_list(field_name, flat=True).distinct()

        for element in listed_unique_values:
            result.update({choice[element][1]: choice[element][1]})

    return result


def get_filter_data_from_list_lookup(field_name, request, source_query, list):
    result = {}
    if field_name in request.GET["filter_data"]:
        listed_unique_values = source_query.values_list(field_name, flat=True).distinct()

        for element in listed_unique_values:
            result.update({list[element]: list[element]})

    return result

def handleGET(request):

    if (request.method == "GET" and request.GET):

        categories = dict(ToyCategory.objects.all().values_list("id", "name"))
        valid_toys = Toy.objects.all().exclude(state=Toy.RETIRED)

        if "filter_data" in request.GET:
            result=get_filter_data_from_choices("state",request,valid_toys,Toy.TOY_STATE_CHOICES)
            if result:
                return JsonResponse(result)

            result=get_filter_data_from_list_lookup("category_id",request,valid_toys,categories)
            if result:
                return JsonResponse(result)

            result = get_filter_data_from_choices("issue_type", request, valid_toys, Toy.ISSUE_TYPE_CHOICES)
            if result:
                return JsonResponse(result)

        if "sort" in request.GET:
            all_records = Toy.objects.all()
            total = all_records.count()

            sort = request.GET.get('sort', 'id')
            order = request.GET.get('order', 'asc')
            limit = int(request.GET.get('limit',total))
            offset = int(request.GET.get('offset',0))
            col_filters = request.GET.get('filter',None)

            if order=="desc":
                dir="-"
            else:
                dir=""

            member_names=dict(Member.objects.all().order_by("id").values_list("id","name"))
            toy_image_files=dict(Image.objects.all().order_by("id").values_list("id","file"))

            if col_filters:
                col_filters=ast.literal_eval(col_filters)

                filter_by_contains('comment',col_filters)
                filter_by_date('borrow_date',col_filters)
                filter_by_contains('code',col_filters)
                filter_by_contains('brand_id',col_filters)
                filter_by_contains('parts_list',col_filters)
                filter_by_choice_lookup('state', Toy.TOY_STATE_CHOICES, col_filters)
                filter_by_date('purchase_date',col_filters)
                filter_by_date('last_stock_take',col_filters)
                filter_by_date('due_date',col_filters)
                filter_by_contains('num_pieces',col_filters)
                filter_by_date('last_check',col_filters)
                filter_by_general('member_loaned_id', 'member_loaned__name__contains', col_filters)
                filter_by_contains('name',col_filters)
                filter_by_choice_lookup('issue_type', Toy.ISSUE_TYPE_CHOICES, col_filters)
                filter_by_general('category_id', 'category__name', col_filters)
                filter_by_contains('purchased_from_id',col_filters)

                total=all_records.filter(**col_filters).count()
                results=all_records.filter(**col_filters).order_by(dir + sort)[offset:offset + limit]
            else:
                results=all_records.order_by(dir+sort)[offset:offset+limit]

            form = ToyIssueForm(toyList=results, user=request.user)

            rows=list(results.values())
            for row in rows:

                format_by_control("issue_comment",form,row)
                format_by_control("issue_type",form, row)
                format_by_control("comment", form, row)


                link = '<button title = "Toy History" type = "button" class="btn btn-link" onclick="getToyHistory(this);" value="{0}">'.format(row["id"])
                link +='<span class ="glyphicon glyphicon-time " aria-hidden="true"></span>'
                link +='</button>'
                link += '<button title = "Toy details" type = "button" class ="btn btn-link" onclick="getToy(this);" value="{0}" >{1}</button>'.format(row["id"], row["code"])
                row["code"] = link


                if row["member_loaned_id"]:
                    link='<button title = "Member details" type = "button" class ="btn btn-link" onclick="getMemberSummary(this);" value="{0}" >{1}</button>'.format(row["member_loaned_id"],member_names[row["member_loaned_id"]])
                    row["member_loaned_id"] = link





                format_by_choice_lookup("state",Toy.TOY_STATE_CHOICES,row)
                format_by_list_lookup("category_id", categories, row)
                format_by_choice_lookup("issue_type", Toy.ISSUE_TYPE_CHOICES, row)
                # format_by_list_lookup("member_loaned_id", member_names, row)
                format_by_date('borrow_date', row)
                format_by_date('purchase_date', row)
                format_by_date('last_stock_take', row)
                format_by_date('due_date', row)
                format_by_date('last_check', row)
                format_by_image('image_id',toy_image_files,row)





            context={"total":total,"rows":rows}

            return JsonResponse(context)
    else:
        return None



class ToyIssueForm(forms.Form):


    def __init__(self, *args, **kwargs):
        toyList=kwargs.pop("toyList", 0)
        user=kwargs.pop("user",0)
        current_user= User.objects.get(username=user.username)

        super(ToyIssueForm, self).__init__(*args, **kwargs)

        if toyList:
            for toy in toyList:
                self.fields['comment_%s' % toy.id] = forms.CharField(required=False, initial=toy.issue_comment,max_length=Toy._meta.get_field('comment').max_length)
                self.fields['issue_comment_%s' % toy.id] = forms.CharField(required=False,initial=toy.issue_comment, max_length=Toy._meta.get_field('issue_comment').max_length)
                if current_user.has_perm("toybox.retire_toy"):
                    self.fields['issue_type_%s' % toy.id] = forms.ChoiceField(required=False,initial=toy.issue_type, choices=Toy.ISSUE_TYPE_CHOICES)
                else:
                    self.fields['issue_type_%s' % toy.id] = forms.ChoiceField(required=False,initial=toy.issue_type, choices=Toy.ISSUE_TYPE_CHOICES[:Toy.RETIRE_VERIFIED])
