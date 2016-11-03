
from django import forms

from toybox.models import *
from django.db.models import Q
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import *


#################
# general helpers
def fragment_search(fragment):
    if fragment != '':
        return Member.objects.filter(Q(name__icontains=fragment)|Q(partner__icontains=fragment)).exclude(active=False).order_by("name")
    else:
        return []


#################
# Context helpers

#def get_memsummary_context(member_id):
#    member = Member.objects.get(pk=mid)
#    #toys = Toy.objects.get(member=mid)
#    context = {'member': member}
#    return context

# Process requests for the member_search frame
def handle_member_search(request):

    possible_members = None
    error=""

    # Search pressed.  Validate form and get list of matching members
    if (request.method == "GET"):
        form = MemberSearchForm(request.GET)
        if form.is_valid():
            name_fragment=form.cleaned_data['member_name_fragment'].strip()
            if name_fragment!="":
                possible_members = fragment_search(name_fragment)

                if possible_members.__len__()==0:
                    error="No members found"
            #else:
                #error="Member name not entered"
            if error!="":
                form.add_error("member_name_fragment",error)
    else:
         form = MemberSearchForm()

    context = {'member_search_form': form,
               'members': possible_members}

    return context


def handle_member_summary(request, member_id):
    context = {}
    if (member_id):
        credit_enable=get_config("credit_enable")
        member = get_object_or_404(Member, pk=member_id)
        children = Child.objects.filter(parent=member_id)
        context = {'member': member,'children': children,'credit_enable':credit_enable}
        #print(context["member"])
    return context



def handle_borrowed_toy_list(request, member_id):
    context = {}
    if (member_id):
        toys=Toy.objects.filter(member_loaned=member_id)

    context = {'toy_list': toys}

    return context

def thisDateTime():
    return timezone.make_aware(datetime.datetime.now(),timezone.get_default_timezone())

def get_members(*fields,**kwargs):
    return {"members":Member.objects.filter(kwargs).values(fields)}

def updateDailyBalance():
    latest_balance=0
    if Transaction.objects.count() >0:
        latest_balance=Transaction.objects.latest().balance
    return {"daily_balance":latest_balance}

def base_data(request):


    context={"version":settings.VERSION}


    context.update(updateDailyBalance())

    context.update(handle_shift(request))

    if 'first_login' not in request.session:
        request.session.update({'first_login':True})
    else:
        context.update({"enable_logout_button":"true"})

    #set till popup for login and kogoff
    if (request.method == "POST"):
        if "till_value" in request.POST:

            if "till_set" in request.POST:
                from toybox.views.transactions import setTill
                try:
                    setTill(request.POST['till_value'],context['daily_balance'],request,"Logon, Logoff")
                except ValueError as e:
                    context.update({"till_value_error":e.message})
                    return context
                else:
                    context.update(updateDailyBalance())


            #for tilll set on login
            if 'first_login' in request.session:
                if request.session['first_login']==True:
                    request.session.update({'first_login':False})
                else:
                     request.session.update({'logout':True})#issue here for transaction page, needs this to set till on logout

    return context


def render_toy_details(request):

    rendered=None
    context={}

    if request.method=="GET":
       if "toy_id" in request.GET:
          toy_id=request.GET["toy_id"]
          toy=Toy.objects.get(id=toy_id)
          context.update({"toy":toy})
          context.update({"MEDIA_URL":settings.MEDIA_URL})
          rendered=render_to_string('toybox/toy_summary.html', context)

    return rendered



def render_toy_history(request):

    rendered=None
    context={}

    if request.method=="GET":
         if "toy_history_id" in request.GET:
            toy_id=request.GET["toy_history_id"]
            context.update({"toy_history":ToyHistory.objects.filter(toy__id=toy_id).order_by('date_time')})
            toy=Toy.objects.get(id=toy_id)
            context.update({"toy":toy})
            rendered=render_to_string('toybox/toy_history.html', context)

    return rendered


def render_member_toy_history(request):

    rendered=None
    context={}

    if request.method=="GET":
         if "toy_history_member_id" in request.GET:
            member_id=request.GET["toy_history_member_id"]
            member_toy_history= ToyHistory.objects.filter(member__id=member_id).order_by('date_time').select_related('toy')
            member=Member.objects.get(id=member_id)
            context.update({"member_toy_history":member_toy_history})
            context.update({"member":member})
            rendered=render_to_string('toybox/member_toy_history.html', context)

    return rendered

def render_member_summary(request):
    rendered = None
    context = {"popup":"true"}

    if request.method == "GET":
        if "member_id" in request.GET:
            member_id = request.GET["member_id"]
            member = Member.objects.get(id=member_id)
            context.update({"member": member})
            rendered = render_to_string('toybox/member_summary.html', context)

    return rendered



def render_ajax_request(request):


    if request.method=="GET" and request.is_ajax():
        #send back rendered toy summary, just data would need to be rendered so it is useless

         if "toy_history_id" in request.GET:
             rendered=render_toy_history(request)
         elif "toy_history_member_id" in request.GET:
             rendered=render_member_toy_history(request)
         elif "toy_id" in request.GET:
             rendered=render_toy_details(request)
         elif "member_id" in request.GET:
             rendered=render_member_summary(request)
         else:
             return None

         return HttpResponse(rendered)

    return None

##################
# Shared form classes
class MemberSearchForm(forms.Form):
    member_name_fragment = forms.CharField(label="Member Name", max_length=20,required=False,widget=forms.TextInput(attrs={'title': 'Enter member name fragment'}))

class ToySearchForm(forms.Form):
    toy_search_string = forms.CharField(label="Exact ID or name fragment of toy to borrow", max_length=100,required=False,widget=forms.TextInput(attrs={'title': 'Enter toy ID or toy name fragment'}))


def get_config(key):

    try:
        value=Config.objects.get(key=key).value.lower()
        value_type=Config.objects.get(key=key).value_type

        # return value

        if value_type == Config.NUMBER:
            try:
                return Decimal(value)
            except:
                raise NameError("Value: "+value+" is not type: "+Config.CONFIG_TYPES[value_type][1])
                return None

        elif value_type == Config.BOOLEAN:
            if value in set(["0","no","n","false"]):
                return False
            elif value in set(["1","yes","y","true"]):
                return True
            else:
                raise NameError("Value: "+value+" is not type: "+Config.CONFIG_TYPES[value_type][1])
                return None

        elif value_type == Config.STRING:
            return value

        else:
            raise NameError("Invalid type")


    except Config.DoesNotExist:

        if key=="credit_enable":
            return(True)

        elif key=="repair_loan_duration":
            return(26)

        elif key=="loan_bond_enable":
            return(True)

        elif key=="default_loan_duration":
            return(2)

        elif key=="max_toys":
            return(4)

        elif key=="loan_durations":
            return(12)

        elif key=="donation_enable":
            return(True)

        elif key=="major_issue_multiplier_min":
            return(0.1)

        elif key=="minor_issue_multiplier_min":
            return(0.0)

        elif key=="major_issue_multiplier_max":
            return(0.5)

        elif key=="minor_issue_multiplier_max":
            return(0.0)

        else:
            raise NameError('Option key not found: '+key)
            return None

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


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

        # for c in choice:
        #     if c[0] in listed_unique_values:
        #         result.update({c[0]:c[1]})
        for element in listed_unique_values:
            result.update({str(choice[element][1]): str(choice[element][1])})

    return result


def get_filter_data_from_list_lookup(field_name, request, source_query, list):
    result = {}
    if field_name in request.GET["filter_data"]:
        listed_unique_values = source_query.order_by(field_name).distinct().values_list(field_name, flat=True)

        for element in listed_unique_values:
            result.update({str(list[element]): str(list[element])})

    return result
def sort_slice_to_rows(request, query, col_filters, Table):


    total = query.count()

    sort = request.GET.get('sort', 'id')
    order = request.GET.get('order', 'asc')
    limit = int(request.GET.get('limit', total))
    offset = int(request.GET.get('offset', 0))

    if order == "desc":
        dir = "-"
    else:
        dir = ""

    if col_filters:
        query = query.filter(**col_filters)
        total=query.count()

    if sort:
        sort_field_type = Table._meta.get_field(sort).get_internal_type()

        if sort_field_type == "CharField":
            query = query.extra(select={sort: 'lower(%s)' % sort}).order_by(dir + sort)
        elif sort_field_type == "ForeignKey":
            query = query.order_by(dir + sort + "__name")
        elif sort_field_type == "IntegerField":
            table=Table()
            table_name = table._meta.db_table
            field=table._meta.get_field_by_name(sort)
            if field[0]._choices:
                choices=field[0]._choices

                sorted_choice = sorted(choices, key=lambda x: x[1])
                db_field_name = '"{0}"."{1}"'.format(table_name,sort)

                i = 0
                #TODO Warning this is native to sqlite, for postgres look up case!!!
                CASE_SQL = '(case '
                for state in sorted_choice:
                    CASE_SQL+= 'when {2}={1} then {0} '.format(i,state[0],db_field_name)
                    i += 1
                CASE_SQL+='end)'

                query = query.extra(select={sort+'_order': CASE_SQL}, order_by=[dir+sort+'_order'])
        else:
            query = query.order_by(dir + sort)

    query = query[offset:offset + limit]
    rows = list(query.values())

    return rows,total

def handle_shift(request):

     context={}
     form=None

     if request.method=="POST":
        form=ShiftForm(request.POST)
        if form.is_valid():

            if "remove_volunteer" in form.data:
                id=int(form.data["remove_volunteer"])
                Shift.objects.get(shift_date=thisDateTime().date(),volunteer=id).delete()
                context.update({"setting_shift":"true"})

            elif "member" in form.data:
                # add volunteer
                context.update({"setting_shift":"true"})
                new_volunteer=form.cleaned_data["member"]
                if new_volunteer:
                    in_shift=Shift.objects.filter(shift_date=thisDateTime().date(),volunteer=new_volunteer)

                    if in_shift.count()==0:
                        shift=Shift(volunteer=new_volunteer,shift_date=thisDateTime().date())
                        shift.save()
                    else:
                        form.add_error("member","volunteer already added")
                else:
                    form.add_error("member","volunteer not selected")

     else:
        form = ShiftForm(request.POST)

     todays_shift=Shift.objects.filter(shift_date=thisDateTime().date()).select_related('volunteer')

     if todays_shift.count()==0:
         todays_shift=None

     context.update({"shift":todays_shift, "shift_form":form})

     return context

class ShiftForm(forms.Form):
    member = forms.ModelChoiceField(required=False, queryset=Member.objects.all().order_by("name"))