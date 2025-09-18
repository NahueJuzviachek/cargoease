# neumaticos/views.py
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CambiarNeumaticosForm
from .selectors import listar_vehiculos_con_neumaticos, listar_almacen, mapear_neumaticos_por_eje
from .services import enviar_a_almacen, montar_en_vehiculo
from .constants import CAPS_POR_TIPO
from .utils import nro_to_pos  # (inyectado en selectors.mapear)

def neumaticos_list(request):
    vehiculos = listar_vehiculos_con_neumaticos()
    almacen = listar_almacen()
    neumaticos_map = mapear_neumaticos_por_eje(vehiculos, nro_to_pos)

    vehiculos_ctx = []
    for v in vehiculos:
        data = neumaticos_map.get(v.id, {"ejes": v.ejes, "por_eje": []})
        vehiculos_ctx.append({"vehiculo": v, "ejes": data["ejes"], "por_eje": data["por_eje"]})

    ctx = {
        "vehiculos_ctx": vehiculos_ctx,
        "almacen": almacen,
        "caps_por_tipo": CAPS_POR_TIPO,
    }
    return render(request, "neumaticos/neumaticos_list.html", ctx)

def neumaticos_cambiar_global(request):
    if request.method != "POST":
        return redirect("neumaticos_list")

    form = CambiarNeumaticosForm(request.POST)
    if not form.is_valid():
        for e in form.errors.values():
            messages.error(request, e.as_text())
        return redirect("neumaticos_list")

    ids = form.cleaned_data["neumaticos_ids"]
    destino = form.cleaned_data["destino"]

    if destino == "almacen":
        moved = enviar_a_almacen(ids)
        messages.success(request, f"{moved} neumático(s) enviados al almacén.")
        return redirect("neumaticos_list")

    if destino.startswith("vehiculo:"):
        try:
            vehiculo_id = int(destino.split(":", 1)[1])
        except ValueError:
            messages.error(request, "Destino de vehículo inválido.")
            return redirect("neumaticos_list")

        eje = form.cleaned_data.get("eje_destino")
        pos = form.cleaned_data.get("posicion_destino")
        auto_asignar = not (eje and pos)

        try:
            moved = montar_en_vehiculo(ids, vehiculo_id, eje, pos, auto_asignar)
        except ValueError as ex:
            messages.error(request, str(ex))
            return redirect("neumaticos_list")

        messages.success(request, f"{moved} neumático(s) montados correctamente.")
        return redirect("neumaticos_list")

    messages.error(request, "Destino no reconocido.")
    return redirect("neumaticos_list")
