from django.shortcuts import render
from django.http import HttpResponse
from .models import Member

def home(request):
    return render(request, 'toybox/landing_page.html', {})

def member_search(request):
    possible_member_names = Member.objects.filter(member_name__startswith=request.GET.get('member_name_frag', ''))
    context = { 'member_names': possible_member_names }
    return render(request, 'toybox/member_search.html', context)

def member_loan(request, member_id):
    return render(request, 'toybox/member_loan.html', { 'member_id': member_id })

# Create your views here.
