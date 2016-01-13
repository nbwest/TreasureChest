from django.shortcuts import render
from django.forms import ModelForm
from shared import *
import django_tables2 as tables
from django.contrib.auth.decorators import login_required

@login_required()
def toys(request):
    context=handle_toy_details(request)
    return render(request, 'toybox/toys.html', context)

def handle_toy_details(request):#, toy_code):
    context={}

    # context.update({"toy_headers":Toy._meta.get_all_field_names()})
    # context.update({"toy_headers":("ID","Name","State","Category","Last Check","Last Stocktake","Checked")})
    context.update({"toys":Toy.objects.all().order_by('code')})

    return context


