from django.shortcuts import render
from shared import *

def home(request):
    return render(request, 'toybox/home.html', {})
