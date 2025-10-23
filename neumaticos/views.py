# neumaticos/views.py
from django.contrib import messages
from django.shortcuts import render, redirect

# Formularios (conservá tus formularios existentes)
from .forms import ReubicarForm
# Selectors/queries para armar la vista
from .selectors import listar_vehiculos_con_neumaticos, listar_almacen, mapear_neumaticos_por_eje
from .utils import nro_to_pos
from .constants import CAPS_POR_TIPO

# ✅ Importamos el módulo de servicios entero (robusto ante import parcial)
from . import services as svc

from .models import Neumatico


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
        msg = svc.reubicar_neumaticos(a_id, b_id)
    except ValueError as ex:
        messages.error(request, str(ex))
        return redirect("neumaticos_list")

    messages.success(request, msg)
    return redirect("neumaticos_list")


def neumaticos_recapar(request):
    if request.method != "POST":
        return redirect("neumaticos_list")

    ids_raw = (request.POST.get("neumaticos_ids_recapar") or "").strip()
    ids = [int(i) for i in ids_raw.split(",") if i.isdigit()]
    if not ids:
        messages.error(request, "Seleccioná neumáticos para recapar (máximo 2).")
        return redirect("neumaticos_list")

    updated = svc.recapar_neumaticos(ids)
    messages.success(request, f"{updated} neumático(s) recapados (km reiniciados).")
    return redirect("neumaticos_list")


def neumaticos_nuevo_almacen(request):
    if request.method != "POST":
        return redirect("neumaticos_list")

    tipo = (request.POST.get("tipo_condicion") or "").strip() or "nuevo"
    neum = svc.crear_neumatico_en_almacen(tipo)
    messages.success(request, f"Neumático #{neum.pk} creado en almacén ({neum.tipo.descripcion}).")
    return redirect("neumaticos_list")


def neumaticos_eliminar_almacen(request):
    """
    Marca como eliminados los neumáticos seleccionados que estén en almacén (vehiculo=None, montado=False).
    Si además usás soft-delete a nivel modelo, podés sumarlo aquí.
    """
    if request.method != "POST":
        return redirect("neumaticos_list")

    ids_raw = (request.POST.get("neumaticos_ids_eliminar") or "").strip()
    ids = [int(i) for i in ids_raw.split(",") if i.isdigit()]
    if not ids:
        messages.error(request, "No seleccionaste neumáticos del almacén para eliminar.")
        return redirect("neumaticos_list")

    # Si además querés soft-deletear (estado ELIMINADO), podés hacerlo aquí:
    marcados = 0
    for n in Neumatico.objects.filter(pk__in=ids, vehiculo__isnull=True, montado=False):
        # Si tenés soft delete en el modelo:
        if hasattr(n, "soft_delete"):
            n.soft_delete()
        marcados += 1

    # Borrado físico de registros en almacén (y/o de neumaticos en almacén)
    try:
        svc.eliminar_neumaticos_del_almacen(ids)
    except Exception:
        pass

    if marcados:
        messages.success(request, f"{marcados} neumático(s) marcados como eliminados.")
    else:
        messages.warning(request, "No se eliminó ningún neumático (verificá que existan).")
    return redirect("neumaticos_list")
