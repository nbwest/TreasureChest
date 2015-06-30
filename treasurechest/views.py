from django.shortcuts import redirect

def base(request):
    return redirect('/toybox', permanent=True) 

