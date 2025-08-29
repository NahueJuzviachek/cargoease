from django.http import JsonResponse
from django.shortcuts import render
from .models import Cliente

# Create your views here.

def clientes(request):
    return render(request, "clientes/clientes.html")

def ListaClientes(request):
    clientes=list(Cliente.objects.values())
    data={'clientes':clientes}
    return JsonResponse(data)
    
    