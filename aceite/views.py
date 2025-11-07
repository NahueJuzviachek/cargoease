from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.template.loader import select_template
from vehiculos.models import Vehiculo
from .models import Aceite, TipoAceite, AceiteCambio
from .forms import CambioAceiteForm
from .services import registrar_cambio_aceite, recalc_km_aceite_para_vehiculo


# ------------------------------
# DASHBOARD PRINCIPAL DE ACEITES
# ------------------------------
def _to_float(x):
    """
    Convierte valores a float de forma segura.
    Acepta Decimal, None o valores numéricos en texto.
    Retorna 0.0 si la conversión falla.
    """
    if x is None:
        return 0.0
    if isinstance(x, Decimal):
        return float(x)
    try:
        return float(x)
    except Exception:
        return 0.0
    

def aceite_dashboard(request, vehiculo_pk: int):
    """
    Vista principal del panel de aceites para un vehículo.
    - Recalcula los kilómetros acumulados para evitar datos desactualizados.
    - Obtiene los registros de aceite de motor y caja.
    - Calcula los valores actuales y máximos de vida útil.
    - Renderiza el panel con la información actualizada.
    """
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_pk)

    # Asegura que los km acumulados estén sincronizados con los viajes del vehículo.
    recalc_km_aceite_para_vehiculo(vehiculo)

    # Recupera ambos aceites del vehículo (motor y caja).
    aceites = {a.tipo: a for a in vehiculo.aceites.all()}
    motor = aceites.get(TipoAceite.MOTOR)
    caja = aceites.get(TipoAceite.CAJA)

    # Prepara valores que el template necesita para las barras de progreso.
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

    # Se intenta usar el primer template disponible entre los listados.
    template = select_template([
        "aceite/aceite_panel.html",
        "aceite/panel.html",
        "vehiculos/aceite_panel.html",
    ])
    return HttpResponse(template.render(context, request))


# ------------------------------
# CONFIRMAR CAMBIO MOTOR / CAJA
# ------------------------------
def confirmar_cambio_motor(request, vehiculo_pk: int):
    """Muestra el formulario de confirmación para cambio de aceite de motor."""
    return _confirmar_cambio(request, vehiculo_pk, TipoAceite.MOTOR)


def confirmar_cambio_caja(request, vehiculo_pk: int):
    """Muestra el formulario de confirmación para cambio de aceite de caja."""
    return _confirmar_cambio(request, vehiculo_pk, TipoAceite.CAJA)


# ------------------------------
# FUNCIONES INTERNAS
# ------------------------------
def _confirmar_cambio(request, vehiculo_pk: int, tipo: str):
    """
    Lógica común para confirmar el cambio de aceite (motor o caja).
    Si el método es POST y el formulario es válido, registra el cambio de aceite
    mediante una transacción atómica y redirige al panel principal.
    """
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_pk)
    try:
        aceite = vehiculo.aceites.get(tipo=tipo)
    except Aceite.DoesNotExist:
        raise Http404("No existe registro de aceite para este tipo.")

    if request.method == "POST":
        form = CambioAceiteForm(request.POST, aceite=aceite)
        if form.is_valid():
            # Se usa una transacción para garantizar consistencia en la actualización.
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
        "aceite/confirm.html",
        "aceite/confirmar.html",
        "vehiculos/aceite_confirm.html",
    ])
    ctx = {"vehiculo": vehiculo, "aceite": aceite, "form": form}
    return HttpResponse(template.render(ctx, request))


# ------------------------------
# BOTONES 'CAMBIAR ACEITE'
# ------------------------------
def cambiar_aceite_motor(request, vehiculo_pk: int):
    """Redirige a la vista de confirmación del cambio de aceite de motor."""
    return _confirmar_cambio(request, vehiculo_pk, TipoAceite.MOTOR)


def cambiar_aceite_caja(request, vehiculo_pk: int):
    """Redirige a la vista de confirmación del cambio de aceite de caja."""
    return _confirmar_cambio(request, vehiculo_pk, TipoAceite.CAJA)


def aceite_cambiar(request, vehiculo_pk: int, tipo: str):
    """
    Redirige dinámicamente según el tipo de aceite recibido ('motor' o 'caja').
    Lanza 404 si el tipo no es válido.
    """
    tipo = (tipo or "").lower()
    if tipo not in ("motor", "caja"):
        raise Http404("Tipo de aceite inválido.")
    return _confirmar_cambio(request, vehiculo_pk, tipo)

def historial_aceites(request, vehiculo_pk):
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_pk)

    # Traemos todos los cambios asociados a aceites de ese vehículo
    cambios = (
        AceiteCambio.objects
        .select_related('aceite')
        .filter(aceite__vehiculo_id=vehiculo_pk)
        .order_by('-fecha')
    )

    context = {
        'vehiculo': vehiculo,
        'cambios': cambios,
    }
    return render(request, 'aceite/historial_aceites.html', context)