
from django import forms

from toybox.models import *
from django.db.models import Q
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import *
from django.db.models.functions import Lower


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
        request.session.pop("page_leave_check", None)
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
    toys=None

    if (member_id):
        toys=Toy.objects.filter(member_loaned=member_id)

    context = {'toy_list': toys}

    # context.update({'toy_details_form':handle_toy_details_form(request,toys)})

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


    context={"version":settings.VERSION, "sandbox":settings.SANDBOX, "development":settings.DEVELOPMENT}


    context.update(updateDailyBalance())



    if 'first_login' not in request.session:
        request.session.update({'first_login':True,'setting_shift':True })
    else:
        context.update({"enable_logout_button":"true"})

    #set till popup for login and kogoff
    if (request.method == "POST"):
        if "till_value" in request.POST:

            if "till_set" in request.POST:

                if request.POST['till_adj_comment'] == "":
                    context.update({"till_comment_error": "Justification is required"})
                    return context

                from toybox.views.transactions import setTill
                try:
                    setTill(request.POST['till_value'],context['daily_balance'],request,"(Logon, Logoff) "+request.POST['till_adj_comment'])
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
    # primarily used for toy pop up - "no_edit" removes ability to edit from popup
    if request.method=="GET":
       if "toy_id" in request.GET:
          toy_id=request.GET["toy_id"]
          toy=Toy.objects.get(id=toy_id)
          context.update({'toy_details_form': handle_toy_details_form(request, [toy])})
          context.update({"toy":toy, "no_edit":True})
          context.update({"MEDIA_URL":settings.MEDIA_URL})
          rendered=render_to_string('toybox/toy_summary.html', context)

    return rendered

def handle_toy_details_form(request,toys, member_id=None):

    form=None

    if (request.method == "POST" and len(toys)>0):
        form = ToyDetailsForm(request.POST, toyList=toys)
        if form.is_valid():

            for key, value in form.cleaned_data.iteritems():


                if key.startswith("issue_type") and value !="":
                    id = key.rpartition('_')[2]
                    toy = Toy.objects.get(pk=id)

                    toy.issue_type = int(value)

                    if "issue_comment_" + id in form.cleaned_data:
                        toy.issue_comment = form.cleaned_data["issue_comment_" + id]

                    if "comment_" + id in form.cleaned_data:
                        toy.comment = form.cleaned_data["comment_" + id]

                    new_toy_state = toy.issue_type_to_state(toy.issue_type)

                    if new_toy_state != None:
                        toy.state=new_toy_state
                        toy_history = ToyHistory()
                        toy_history.record_toy_event(toy, request.user, thisDateTime().now())

                    toy.save()

            if member_id!=None:
                new_borrow_list = TempBorrowList.objects.filter(member__id=member_id)
                toys = []
                for item in new_borrow_list:
                    toys.append(item.toy)

            form = ToyDetailsForm(request.POST, toyList=toys)

    if not form:
        form = ToyDetailsForm(toyList=toys)

    return form


class ToyDetailsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        toyList = kwargs.pop("toyList", [None])
        super(ToyDetailsForm, self).__init__(*args, **kwargs)

        for toy in toyList:
            if toy:
                self.fields['comment_%s' % toy.id] = forms.CharField(required=False, initial=toy.comment,max_length=Toy._meta.get_field('comment').max_length)
                self.fields['issue_type_%s' % toy.id] = forms.ChoiceField(required=False, initial=toy.issue_type,choices=Toy.ISSUE_TYPE_CHOICES[:Toy.WHOLE_TOY_MISSING])
                self.fields['issue_comment_%s' % toy.id] = forms.CharField(required=False, initial=toy.issue_comment,max_length=Toy._meta.get_field('comment').max_length)




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


    # if request.method=="GET" and request.is_ajax():
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

    # return None

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


        elif value_type == Config.BOOLEAN:
            if value in set(["0","no","n","false"]):
                return False
            elif value in set(["1","yes","y","true"]):
                return True
            else:
                raise NameError("Value: "+value+" is not type: "+Config.CONFIG_TYPES[value_type][1])


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
            return(10)

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

        elif key == "membership_warning_duration":
            return (60)

        elif key == "minimum_member_bond":
            return (5.0)
        else:
            raise NameError('Option key not found: '+key)


def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


def filter_by_contains(field_name, filters):
    if field_name in filters:
        if filters[field_name] != "":
            filters.update({field_name+"__icontains": filters[field_name]})
        filters.pop(field_name)

def filter_by_date(field_name,filters):
    if field_name in filters:
        if filters[field_name] != "":
            dt = datetime.datetime.strptime(filters[field_name], "%d/%m/%y")
            filters.update({field_name+"__startswith": dt.date()})
        filters.pop(field_name)

def filter_by_general(field_name, query, filters):
    if field_name in filters:
        if filters[field_name] != "":
            filters.update({query: filters[field_name]})
        filters.pop(field_name)


def filter_by_choice_lookup(field_name, choices, filters):
    if field_name in filters:
        if filters[field_name] != "":
            for choice in choices:
                if filters[field_name]==choice[1]:
                   filters.update({field_name:choice[0]})
                   return



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

def format_by_image(field_name,list,row,caption=None):
    if row[field_name]:
        row[field_name] = '<a href = "{0}{1}" ><img class ="img-thumbnail"  style="image-orientation:from-image; " src="{0}{1}" ></a>'.format(settings.MEDIA_URL, list[row[field_name]])

    if caption:
        row[field_name] +='<p>'+caption+'</p>'
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

def get_filter_data_direct(field_name, request, dic):
    result = {}
    if field_name == request.GET["filter_data"]:
        result=dic
    return result

def sort_slice_to_rows(request, query, col_filters, Table, foreignkey_sort="__name"):

    total = query.count()
    limit = int(request.GET.get('limit', total))
    offset = int(request.GET.get('offset', 0))

    total,query=sort_to_rows(request, query, col_filters, Table, foreignkey_sort)

    query = query[offset:offset + limit]

    return total,query

def sort_to_rows(request, query, col_filters, Table, foreignkey_sort="__name"):
    total = query.count()

    sort = request.GET.get('sort', 'id')
    order = request.GET.get('order', 'asc')

    if order == "desc":
        dir = "-"
    else:
        dir = ""


    if col_filters:
        query = query.filter(**col_filters)
        total = query.count()

    if sort:
        try:
            sort_field_type = Table._meta.get_field(sort).get_internal_type()
        except:
            try:
                query = query.order_by(dir + sort)
            except:
                print "Invalid field"
        else:
            if sort_field_type == "CharField":
                # query = query.extra(select={sort: 'lower(%s)' % sort}).order_by(dir + sort)
                if order=="desc":
                    query = query.order_by(Lower(sort).desc())
                else:
                    query = query.order_by(Lower(sort).asc())

            elif sort_field_type == "ForeignKey":
                query = query.order_by(dir + sort + foreignkey_sort)
            elif sort_field_type == "IntegerField":
                table = Table()
                table_name = table._meta.db_table
                field = table._meta.get_field_by_name(sort)
                #needed to sort by the alphabetical order of the choices - bootstrap table forces alphabetical order in drop down
                if field[0]._choices:
                    choices = field[0]._choices

                    sorted_choice = sorted(choices, key=lambda x: x[1])
                    db_field_name = '"{0}"."{1}"'.format(table_name, sort)

                    i = 0
                    # TODO Warning this is native to sqlite, for postgres look up case!!!
                    CASE_SQL = '(case '
                    for state in sorted_choice:
                        CASE_SQL += 'when {2}={1} then {0} '.format(i, state[0], db_field_name)
                        i += 1
                    CASE_SQL += 'end)'

                    query = query.extra(select={sort + '_order': CASE_SQL}, order_by=[dir + sort + '_order'])
                else:
                    query = query.order_by(dir + sort)
            else:
                query = query.order_by(dir + sort)
    return total,query





