from django.shortcuts import render
from django.forms import ModelForm
from shared import *


def toys(request, toy_id=None):
    context={}
    context.update(base_data())
    context.update(handle_toy_details(request, toy_id))
    context.update(handle_toy_history(request,toy_id))

    toy_list=Toy.objects.all().order_by('code')

    context.update(handle_stocktake(request))

    form=ToyIssueForm(toyList=toy_list)
    context.update({"toy_issue_form":form})

    context.update({"toys":toy_list})

    return render(request, 'toybox/toys.html', context)

def handle_stocktake(request):
    context={}

    #TODO have ability to update issue and issue comment
    if request.method=="POST":
        if "btn_stocktake_checked" in request.POST:
            for key,value in request.POST.iteritems():

                if key=="stocktake" in request.POST:
                    selected=request.POST.getlist('stocktake')
                    for item in selected:
                      toy=Toy.objects.get(pk=int(item))
                      toy.last_stock_take=datetime.datetime.now()
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
                    toy_history.record_toy_event(toy)
                    if "issue_comment_"+id in request.POST:
                        toy.issue_comment=request.POST["issue_comment_"+id]
                    toy.save()

                elif key.startswith("issue_comment"):
                    id=key.rpartition('_')[2]
                    if not "issue_type_"+id in request.POST:
                        toy=Toy.objects.get(pk=id)
                        toy.issue_comment=value
                        toy_history=ToyHistory()
                        toy_history.record_toy_event(toy)
                        toy.save()

    return(context)


def handle_toy_details(request, toy_id):

    context={}
    if request.method=="GET":
        if toy_id:
            toy = get_object_or_404(Toy, pk=toy_id)
            context.update({"toy":toy})

    return context


def handle_toy_history(request, toy_id):

    context={}
    context.update({"toy_history":ToyHistory.objects.filter(toy__id=toy_id).order_by('date_time')})

    # print(context)
    return context


class ToyIssueForm(forms.Form):


    def __init__(self, *args, **kwargs):
        toyList=kwargs.pop("toyList", 0)
        super(ToyIssueForm, self).__init__(*args, **kwargs)

        if toyList:
            for toy in toyList:
                self.fields['issue_comment_%s' % toy.id] = forms.CharField(required=False,initial=toy.issue_comment, max_length=ToyHistory._meta.get_field('issue_comment').max_length)
                self.fields['issue_type_%s' % toy.id] = forms.ChoiceField(required=False,initial=toy.issue_type, choices=Toy.ISSUE_TYPE_CHOICES)
