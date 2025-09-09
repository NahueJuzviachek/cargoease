from django.shortcuts import render

def ViajesListView(request):
    return render(request, 'viajes/viajes_list.html')
