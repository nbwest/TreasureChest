from django.shortcuts import render
from shared import *

def home(request):
    context={}
    context.update(base_data())
    return render(request, 'toybox/home.html', context)
