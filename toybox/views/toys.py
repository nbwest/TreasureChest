from shared import *
from django.contrib.auth.decorators import login_required
from math import ceil
from django.shortcuts import *
from django.template.loader import render_to_string

# Provide estimate of borrow cost based on purchase cost
# Calculates 1% of purchase cost rounded up to nearest $0.50
def estimate_borrow_cost(purchase_cost):
    onepc = float(purchase_cost)/100.0
    return 0.5 * ceil(2.0 * onepc)


@login_required()
def toys(request, toy_id=None):

    context = {"title":"Toys"}

    loan_bond_enable= get_config("loan_bond_enable")
    context.update({"loan_bond_enable":loan_bond_enable})

    context.update(base_data(request))
    context.update(handle_toy_details(request, toy_id))
    context.update(handle_toy_history(request,toy_id))

    if request.is_ajax():
        #send back rendered toy summary, just data would need to be rendered so it is useless
         context.update({"MEDIA_URL":settings.MEDIA_URL})
         rendered=render_to_string('toybox/toy_summary.html', context)
         return HttpResponse(rendered)

    else:
        toy_list=Toy.objects.filter(~Q(state=Toy.RETIRED)).select_related('category').select_related('member_loaned')
        context.update(handle_stocktake(request))
        form=ToyIssueForm(toyList=toy_list, user=request.user)
        context.update({"toy_issue_form":form})
        context.update({"toys":toy_list})

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


def handle_toy_details(request, toy_id):

    context={}

    if request.method=="GET":
       if "toy_id" in request.GET:
          id=request.GET["toy_id"]
          toy=Toy.objects.get(id=id)
          context.update({"toy":toy})

    return context


def handle_toy_history(request, toy_id):

    context={}
    context.update({"toy_history":ToyHistory.objects.filter(toy__id=toy_id).order_by('date_time')})

    return context


class ToyIssueForm(forms.Form):


    def __init__(self, *args, **kwargs):
        toyList=kwargs.pop("toyList", 0)
        user=kwargs.pop("user",0)
        current_user= User.objects.get(username=user.username)

        super(ToyIssueForm, self).__init__(*args, **kwargs)

        if toyList:
            for toy in toyList:
                self.fields['issue_comment_%s' % toy.id] = forms.CharField(required=False,initial=toy.issue_comment, max_length=ToyHistory._meta.get_field('issue_comment').max_length)
                if current_user.has_perm("toy.retire_toy"):
                    self.fields['issue_type_%s' % toy.id] = forms.ChoiceField(required=False,initial=toy.issue_type, choices=Toy.ISSUE_TYPE_CHOICES)
                else:
                    self.fields['issue_type_%s' % toy.id] = forms.ChoiceField(required=False,initial=toy.issue_type, choices=Toy.ISSUE_TYPE_CHOICES[:Toy.RETIRE_VERIFIED])
