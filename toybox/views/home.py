from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from toybox.views.shared import base_data


@login_required
def home(request):
    context = {"title":"Toy Library"}
    context.update(base_data(request))
    return render(request, 'toybox/home.html', context)
