from django.shortcuts import render
from django.forms import ModelForm
from shared import *


def toys(request, toy_id=None):
    context={}

    context.update(handle_toy_details(request, toy_id))

    context.update({"toys":Toy.objects.all().order_by('code')})

    return render(request, 'toybox/toys.html', context)


def handle_toy_details(request, toy_id):

    context={}
    if request.method=="GET":
        if toy_id:
            toy = get_object_or_404(Toy, pk=toy_id)
            context.update({"toy":toy})

    return context


