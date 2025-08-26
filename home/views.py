from django.shortcuts import render, HttpResponse

# Create your views here.

def home(request):
    
    return HttpResponse("home")

def clientes(request):
    
    return HttpResponse("clientes")

def conductores(request):
    
    return HttpResponse("conductores")

def vehiculos(request):
    
    return HttpResponse("vehiuclos")

def reportes(request):
    
    return HttpResponse("reportes")