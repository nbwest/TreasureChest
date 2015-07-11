from django.shortcuts import render
from shared import *

def home(request):
    return render(request, 'toybox/landing_page.html', {})

#########################
# Unimplemented workflows
def returns(request):
    context = get_memsearch_context(request)
    return render(request, 'toybox/returns.html', context)

def membership_admin(request):
    context = get_memsearch_context(request)
    return render(request, 'toybox/membership_admin.html', context)

def end_of_day(request):
    return render(request, 'toybox/end_of_day.html')
