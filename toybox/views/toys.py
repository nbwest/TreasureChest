from django.shortcuts import render
from django.forms import ModelForm
from shared import *


def toys(request, toy_code=None):
    context={}

    context.update(handle_toy_details(request, toy_code))

    context.update({"toys":Toy.objects.all().order_by('code')})

    return render(request, 'toybox/toys.html', context)


def handle_toy_details(request, toy_code):

    context={}
    if request.method=="GET":
        if toy_code:
            toy = get_object_or_404(Toy, code=toy_code)
            context.update({"toy":toy})

    return context


