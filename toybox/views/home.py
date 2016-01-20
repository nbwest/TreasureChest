from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home(request):
    context={}
    context.update(base_data(request))
    return render(request, 'toybox/home.html', context)
