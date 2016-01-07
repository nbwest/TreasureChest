from django.shortcuts import render
from django.forms import ModelForm
from shared import *


def toys(request, toy_id=None):
    context={}
    context.update(base_data())
    context.update(handle_toy_details(request, toy_id))
    context.update(handle_toy_history(request,toy_id))

    handle_stocktake(request)


    context.update({"toys":Toy.objects.all().order_by('code')})

    return render(request, 'toybox/toys.html', context)

def handle_stocktake(request):

    if request.method=="POST":
        if "stocktake" in request.POST:
            selected=request.POST.getlist('stocktake')
            for item in selected:
              toy=Toy.objects.get(pk=int(item))
              toy.last_stock_take=datetime.datetime.now()
              toy.save()



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