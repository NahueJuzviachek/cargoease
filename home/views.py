from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required

#@login_required
def home(request):
    return render(request, "home/home.html")

def conductores(request):
    return render(request, "home/conductores.html")

def vehiculos(request):
    return render(request, "home/vehiculos.html")

def reportes(request):
    return render(request, "home/reportes.html")

