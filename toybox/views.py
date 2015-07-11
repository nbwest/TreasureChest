from django.shortcuts import render
from django.http import HttpResponse
from .models import Member, Toy

def home(request):
    return render(request, 'toybox/landing_page.html', {})


#################
# general helpers
def fragment_search(fragment):
    if fragment != '':
        return Member.objects.filter(name__contains=fragment)
    else:
        return []

#################
# Context helpers
def get_memsearch_context(request):
    possible_members = fragment_search(request.GET.get('member_name_frag', ''))
    context = { 'members': possible_members }
    return context

def get_memsummary_context(mid):
    member = Member.objects.get(pk=mid)
    toys = Toy.objects.get(member=mid)
    context = { 'member': member,
                'toys': toys } 
    return context


#####################
# Workflow root views
def loans(request, member_id=0):
    context = get_memsearch_context(request)
    if member_id != 0:
        context.update(get_memsummary_context(member_id))
    return render(request, 'toybox/loans.html', context)

def returns(request):
    context = get_memsearch_context(request)
    return render(request, 'toybox/returns.html', context)

def membership_admin(request):
    context = get_memsearch_context(request)
    return render(request, 'toybox/membership_admin.html', context)

def end_of_day(request):
    return render(request, 'toybox/end_of_day.html')


##################
# Other views
def member_loan(request, member_id):
    return render(request, 'toybox/member_loan.html', { 'member_id': member_id })

def member_search(request):
    context = get_memsearch_context(request)
    return render(request, 'toybox/member_search.html', context)

