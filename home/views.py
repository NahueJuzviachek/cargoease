from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required

#@login_required
def home(request):
    return render(request, "home/home.html")



def reportes(request):
    return render(request, "home/soporte.html")

