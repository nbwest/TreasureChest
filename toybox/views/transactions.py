from django.shortcuts import render
from shared import *


def transactions(request):
    return render(request, 'toybox/transactions.html', {})
