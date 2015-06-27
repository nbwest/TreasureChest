from django.shortcuts import render
from django.http import HttpResponse
from .models import Member

def home(request):
    return render(request, 'toybox/landing_page.html', {})

def fragment_search(fragment):
    if fragment != '':
        return Member.objects.filter(member_name__contains=fragment) 
    else:
        return []

def get_memsearch_context(request):
    possible_member_names = fragment_search(request.GET.get('member_name_frag', '')) 
    context = { 'member_names': possible_member_names }
    return context

def member_search(request):
    context = get_memsearch_context(request)
    return render(request, 'toybox/member_search.html', context)

def member_loan(request, member_id):
    return render(request, 'toybox/member_loan.html', { 'member_id': member_id })

# Create your views here.
def loans(request):
    context = get_memsearch_context(request)
    return render(request, 'toybox/loans.html', context)

def returns(request):
    context = get_memsearch_context(request)
    return render(request, 'toybox/returns.html', context)

def membership_admin(request):
    context = get_memsearch_context(request)
    return render(request, 'toybox/membership_admin.html', context)

def end_of_day(request):
    return render(request, 'toybox/end_of_day.html')
