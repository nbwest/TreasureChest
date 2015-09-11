from django.shortcuts import render
from shared import *

def toys(request):
    return render(request, 'toybox/toys.html', {})
