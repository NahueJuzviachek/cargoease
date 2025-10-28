from django.contrib import messages
from django.shortcuts import render, redirect

# Formularios para operaciones de neumáticos
from .forms import ReubicarForm
# Funciones auxiliares para listar y mapear datos de neumáticos
from .selectors import listar_vehiculos_con_neumaticos, listar_almacen, mapear_neumaticos_por_eje
from .utils import nro_to_pos
from .constants import CAPS_POR_TIPO

# Importa todos los servicios del módulo para operaciones robustas
from . import services as svc

from .models import Neumatico


# =========================
# Lista de neumáticos
# =========================
def neumaticos_list(request):
    """
    Renderiza la vista principal de neumáticos:
    - Lista de vehículos con sus neumáticos por eje
    - Inventario de neumáticos en almacén
    - Capacidades por tipo de neumático
    """
    vehiculos = listar_vehiculos_con_neumaticos()
    almacen = listar_almacen()
    neumaticos_map = mapear_neumaticos_por_eje(vehiculos, nro_to_pos)

    # Construye contexto de vehículos con sus neumáticos por eje
    vehiculos_ctx = []
    for v in vehiculos:
        data = neumaticos_map.get(v.id, {"ejes": v.ejes, "por_eje": []})
        vehiculos_ctx.append({"vehiculo": v, "ejes": data["ejes"], "por_eje": data["por_eje"]})

    return render(request, "neumaticos/neumaticos_list.html", {
        "vehiculos_ctx": vehiculos_ctx,
        "almacen": almacen,
        "caps_por_tipo": CAPS_POR_TIPO,
    })


# =========================
# Reubicar neumáticos
# =========================
def neumaticos_reubicar(request):
    """
    Intercambia la ubicación de dos neumáticos.
    - Método: POST
    - Usa el formulario ReubicarForm
    """
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


# =========================
# Recapar neumáticos
# =========================
def neumaticos_recapar(request):
    """
    Reinicia los km de neumáticos seleccionados (máx. 2) como parte del proceso de recapado.
    - Método: POST
    """
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


# =========================
# Crear neumático en almacén
# =========================
def neumaticos_nuevo_almacen(request):
    """
    Crea un neumático nuevo en el almacén.
    - Método: POST
    - 'tipo_condicion' define si es nuevo, usado, etc.
    """
    if request.method != "POST":
        return redirect("neumaticos_list")

    tipo = (request.POST.get("tipo_condicion") or "").strip() or "nuevo"
    neum = svc.crear_neumatico_en_almacen(tipo)
    messages.success(request, f"Neumático #{neum.pk} creado en almacén ({neum.tipo.descripcion}).")
    return redirect("neumaticos_list")


# =========================
# Eliminar neumático del almacén
# =========================
def neumaticos_eliminar_almacen(request):
    """
    Marca neumáticos como eliminados en el almacén.
    - Solo neumáticos que no estén montados en vehículos (vehiculo=None, montado=False)
    - Soporta soft-delete si el modelo tiene implementado 'soft_delete'
    """
    if request.method != "POST":
        return redirect("neumaticos_list")

    ids_raw = (request.POST.get("neumaticos_ids_eliminar") or "").strip()
    ids = [int(i) for i in ids_raw.split(",") if i.isdigit()]
    if not ids:
        messages.error(request, "No seleccionaste neumáticos del almacén para eliminar.")
        return redirect("neumaticos_list")

    # Marca neumáticos como eliminados (soft delete si existe)
    marcados = 0
    for n in Neumatico.objects.filter(pk__in=ids, vehiculo__isnull=True, montado=False):
        if hasattr(n, "soft_delete"):
            n.soft_delete()
        marcados += 1

    # Eliminación física en almacén mediante servicio
    try:
        svc.eliminar_neumaticos_del_almacen(ids)
    except Exception:
        pass

    # Mensajes según resultado
    if marcados:
        messages.success(request, f"{marcados} neumático(s) marcados como eliminados.")
    else:
        messages.warning(request, "No se eliminó ningún neumático (verificá que existan).")
    return redirect("neumaticos_list")
