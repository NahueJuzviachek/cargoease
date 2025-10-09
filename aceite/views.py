from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.template.loader import select_template
from django.http import HttpResponse
from vehiculos.models import Vehiculo
from .models import Aceite, TipoAceite
from .forms import CambioAceiteForm
from .services import registrar_cambio_aceite, recalc_km_aceite_para_vehiculo


# ------------------------------
# DASHBOARD PRINCIPAL DE ACEITES
# ------------------------------
def _to_float(x):
    if x is None:
        return 0.0
    if isinstance(x, Decimal):
        return float(x)
    try:
        return float(x)
    except Exception:
        return 0.0
    

def aceite_dashboard(request, vehiculo_pk: int):
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_pk)
    # Recalcular para evitar datos viejos
    recalc_km_aceite_para_vehiculo(vehiculo)

    # Traemos ambos aceites
    aceites = {a.tipo: a for a in vehiculo.aceites.all()}
    motor = aceites.get(TipoAceite.MOTOR)
    caja = aceites.get(TipoAceite.CAJA)

    # Valores que el template espera
    km_motor = _to_float(getattr(motor, "km_acumulados", 0))
    km_caja = _to_float(getattr(caja, "km_acumulados", 0))
    max_motor = int(getattr(motor, "vida_util_km", 30000)) if motor else 30000
    max_caja = int(getattr(caja, "vida_util_km", 100000)) if caja else 100000

    context = {
        "vehiculo": vehiculo,
        "motor": motor,
        "caja": caja,
        "km_motor": km_motor,
        "km_caja": km_caja,
        "max_motor": max_motor,
        "max_caja": max_caja,
    }

    template = select_template([
        "aceite/aceite_panel.html",  # tu nombre
        "aceite/panel.html",         # fallback
        "vehiculos/aceite_panel.html",
    ])
    return HttpResponse(template.render(context, request))

# ------------------------------
# CONFIRMAR CAMBIO MOTOR / CAJA
# ------------------------------
def confirmar_cambio_motor(request, vehiculo_pk: int):
    return _confirmar_cambio(request, vehiculo_pk, TipoAceite.MOTOR)


def confirmar_cambio_caja(request, vehiculo_pk: int):
    return _confirmar_cambio(request, vehiculo_pk, TipoAceite.CAJA)


# ------------------------------
# FUNCIONES INTERNAS
# ------------------------------
def _confirmar_cambio(request, vehiculo_pk: int, tipo: str):
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_pk)
    try:
        aceite = vehiculo.aceites.get(tipo=tipo)
    except Aceite.DoesNotExist:
        raise Http404("No existe registro de aceite para este tipo.")

    if request.method == "POST":
        form = CambioAceiteForm(request.POST, aceite=aceite)
        if form.is_valid():
            with transaction.atomic():
                registrar_cambio_aceite(
                    aceite,
                    filtros_cambiados=form.cleaned_data.get("filtros_cambiados", False),
                )
            messages.success(
                request,
                f"Se registró el cambio de aceite de {aceite.get_tipo_display()} "
                f"en {vehiculo}. Ciclo #{aceite.ciclos} iniciado.",
            )
            return redirect(reverse("vehiculo_aceite", kwargs={"vehiculo_pk": vehiculo.pk}))
    else:
        form = CambioAceiteForm(aceite=aceite)

    template = select_template([
        "aceite/confirm.html",        # <-- tu nombre
        "aceite/confirmar.html",
        "vehiculos/aceite_confirm.html",
    ])
    ctx = {"vehiculo": vehiculo, "aceite": aceite, "form": form}
    return HttpResponse(template.render(ctx, request))

# ------------------------------
# BOTONES 'CAMBIAR ACEITE'
# ------------------------------
def cambiar_aceite_motor(request, vehiculo_pk: int):
    """Redirige a la confirmación del cambio de aceite de motor."""
    return _confirmar_cambio(request, vehiculo_pk, TipoAceite.MOTOR)


def cambiar_aceite_caja(request, vehiculo_pk: int):
    """Redirige a la confirmación del cambio de aceite de caja."""
    return _confirmar_cambio(request, vehiculo_pk, TipoAceite.CAJA)

def aceite_cambiar(request, vehiculo_pk: int, tipo: str):
    tipo = (tipo or "").lower()
    if tipo not in ("motor", "caja"):
        raise Http404("Tipo de aceite inválido.")
    # Reusa la lógica ya implementada
    return _confirmar_cambio(request, vehiculo_pk, tipo)