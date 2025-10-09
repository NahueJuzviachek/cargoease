from django.shortcuts import render
from .forms import formularioSoporte

from django.contrib.auth.decorators import login_required

#@login_required

def soporte(request):
    formulario_soporte=formularioSoporte()
    return render(request, 'soporte/soporte.html', {'miSoporte':formulario_soporte})

