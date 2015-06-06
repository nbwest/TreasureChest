#from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("<h1>Welcome to Megs Toy Box</h1> ToyBox home search")

def member(request, member_id):
    response = "Member details for member: %s\n"
    return HttpResponse(response % member_id)

# Create your views here.
