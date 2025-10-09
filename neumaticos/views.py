# neumaticos/views.py
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CambiarNeumaticosForm, ReubicarForm
from .selectors import listar_vehiculos_con_neumaticos, listar_almacen, mapear_neumaticos_por_eje
from .services import (
    enviar_a_almacen, montar_en_vehiculo, crear_neumatico_en_almacen,
    eliminar_neumaticos_del_almacen, recapar_neumaticos, reubicar_neumaticos
)

from .constants import CAPS_POR_TIPO
from .utils import nro_to_pos


def neumaticos_list(request):
    vehiculos = listar_vehiculos_con_neumaticos()
    almacen = listar_almacen()
    neumaticos_map = mapear_neumaticos_por_eje(vehiculos, nro_to_pos)

    vehiculos_ctx = []
    for v in vehiculos:
        data = neumaticos_map.get(v.id, {"ejes": v.ejes, "por_eje": []})
        vehiculos_ctx.append({"vehiculo": v, "ejes": data["ejes"], "por_eje": data["por_eje"]})

    return render(request, "neumaticos/neumaticos_list.html", {
        "vehiculos_ctx": vehiculos_ctx,
        "almacen": almacen,
        "caps_por_tipo": CAPS_POR_TIPO,
    })

def neumaticos_reubicar(request):
    if request.method != "POST":
        return redirect("neumaticos_list")

    form = ReubicarForm(request.POST)
    if not form.is_valid():
        for e in form.errors.values():
            messages.error(request, e.as_text())
        return redirect("neumaticos_list")

    a_id, b_id = form.cleaned_data["neumaticos_ids_swap"]
    try:
        msg = reubicar_neumaticos(a_id, b_id)
    except ValueError as ex:
        messages.error(request, str(ex))
        return redirect("neumaticos_list")

    messages.success(request, msg)
    return redirect("neumaticos_list")

# Las vistas de recapar / eliminar / nuevo en almacén se mantienen igual
def neumaticos_recapar(request):
    if request.method != "POST":
        return redirect("neumaticos_list")
    ids_raw = (request.POST.get("neumaticos_ids_recapar") or "").strip()
    ids = [int(i) for i in ids_raw.split(",") if i.isdigit()]
    if not ids:
        messages.error(request, "Seleccioná neumáticos para recapar (máximo 2).")
        return redirect("neumaticos_list")
    updated = recapar_neumaticos(ids)
    messages.success(request, f"{updated} neumático(s) recapados (km reiniciados).")
    return redirect("neumaticos_list")

def neumaticos_nuevo_almacen(request):
    if request.method != "POST":
        return redirect("neumaticos_list")
    tipo = (request.POST.get("tipo_condicion") or "").strip() or "nuevo"
    neum = crear_neumatico_en_almacen(tipo)
    messages.success(request, f"Neumático #{neum.pk} creado en almacén ({neum.tipo.descripcion}).")
    return redirect("neumaticos_list")

def neumaticos_eliminar_almacen(request):
    if request.method != "POST":
        return redirect("neumaticos_list")
    ids_raw = (request.POST.get("neumaticos_ids_eliminar") or "").strip()
    ids = [int(i) for i in ids_raw.split(",") if i.isdigit()]
    if not ids:
        messages.error(request, "No seleccionaste neumáticos del almacén para eliminar.")
        return redirect("neumaticos_list")
    deleted = eliminar_neumaticos_del_almacen(ids)
    if deleted:
        messages.success(request, f"Eliminados {deleted} neumático(s) del almacén.")
    else:
        messages.warning(request, "No se eliminaron neumáticos (verificá que estén en almacén).")
    return redirect("neumaticos_list")
