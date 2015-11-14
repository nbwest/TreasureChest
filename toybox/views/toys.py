from django.shortcuts import render
from django.forms import ModelForm
from shared import *


def toys(request, toy_code=None):
    context=handle_toy_details(request, toy_code)
    return render(request, 'toybox/toys.html', context)

def handle_toy_details(request, toy_code):#, toy_code):
    context={}

    # context.update({"toy_headers":Toy._meta.get_all_field_names()})
    # context.update({"toy_headers":("ID","Name","State","Category","Last Check","Last Stocktake","Checked")})

    if request.method=="GET":
        if toy_code:
            toy = get_object_or_404(Toy, code=toy_code)
            context.update({"toy":toy})

    context.update({"toys":Toy.objects.all().order_by('code')})

    return context


