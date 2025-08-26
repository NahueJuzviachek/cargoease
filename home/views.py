from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required

#@login_required
def home(request):
    return render(request, "home/home.html")

def clientes(request):
    return render(request, "clientes.html")
    
def conductores(request):
    return render(request, "conductores.html")

def login(request):
    return render(request, "login.html")

def vehiculos(request):
    return render(request, "vehiculos.html")

def reportes(request):
    return render(request, "reportes.html")

