from django.shortcuts import render
from shared import *

def reports(request):
    return render(request, 'toybox/reports.html', {})
