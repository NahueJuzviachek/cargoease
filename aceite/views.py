# aceite/views.py
from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST

from vehiculos.models import Vehiculo
from .models import Aceite, EstadoAceite, TipoAceite
from .services import cambiar_aceite, recalc_km_aceite_para_vehiculo

MAX_MOTOR = 30000
MAX_CAJA = 100000

def _suma_km_viajes(vehiculo):
    # Evitamos import circular aquí
    from viajes.models import Viaje
    total = Viaje.objects.filter(vehiculo=vehiculo).aggregate(s=Sum("distancia"))["s"]
    return Decimal(total or 0)


def _ensure_aceite_en_uso(vehiculo, tipo: str, vida_default: int = 15000) -> Aceite:
    """
    Garantiza que exista 1 registro 'en uso' por tipo para el vehículo.
    Si no existe, lo crea tomando snapshot del total de km de viajes actual.
    """
    aceite = Aceite.objects.filter(
        vehiculo=vehiculo,
        tipo=tipo,
        estado=EstadoAceite.EN_USO,
    ).first()
    if not aceite:
        snapshot = _suma_km_viajes(vehiculo)
        aceite = Aceite.objects.create(
            vehiculo=vehiculo,
            tipo=tipo,
            viajes_km_acumulados_al_instalar=snapshot,
            km_acumulados=Decimal("0"),
            vida_util_km=vida_default,
            estado=EstadoAceite.EN_USO,
        )
    return aceite


def aceite_dashboard(request, vehiculo_pk: int):
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_pk)

    motor = _ensure_aceite_en_uso(vehiculo, TipoAceite.MOTOR)
    caja = _ensure_aceite_en_uso(vehiculo, TipoAceite.CAJA)

    # Recalcular por si se agregaron/editaron/borraron viajes
    recalc_km_aceite_para_vehiculo(vehiculo)
    motor.refresh_from_db()
    caja.refresh_from_db()

    km_motor = float(motor.km_acumulados or 0)
    km_caja = float(caja.km_acumulados or 0)
    pct_motor_cap = min(100.0, (km_motor / MAX_MOTOR) * 100.0) if MAX_MOTOR else 0.0
    pct_caja_cap  = min(100.0, (km_caja  / MAX_CAJA)  * 100.0) if MAX_CAJA  else 0.0

    ctx = {
        "vehiculo": vehiculo,
        "motor": motor,
        "caja": caja,

        # km actuales
        "km_motor": motor.km_acumulados,
        "km_caja": caja.km_acumulados,

        # máximos fijos para UI (gráfico + barras)
        "max_motor": MAX_MOTOR,
        "max_caja": MAX_CAJA,

        # porcentajes vs máximos fijos
        "pct_motor_cap": pct_motor_cap,
        "pct_caja_cap": pct_caja_cap,
    }
    return render(request, "aceite/aceite_panel.html", ctx)


@require_POST
def cambiar_aceite_motor(request, vehiculo_pk: int):
    """
    Registra cambio de aceite de MOTOR.
    Lee checkbox 'filtros_cambiados' del POST.
    """
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_pk)
    motor = _ensure_aceite_en_uso(vehiculo, TipoAceite.MOTOR)
    filtros = request.POST.get("filtros_cambiados") == "on"
    cambiar_aceite(motor, notas=request.POST.get("notas", ""), filtros_cambiados=filtros)
    messages.success(request, "Cambio de aceite de motor registrado. Contador de km reseteado.")
    return redirect("vehiculo_aceite", vehiculo_pk=vehiculo.pk)


@require_POST
def cambiar_aceite_caja(request, vehiculo_pk: int):
    """
    Registra cambio de aceite de CAJA.
    """
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_pk)
    caja = _ensure_aceite_en_uso(vehiculo, TipoAceite.CAJA)
    cambiar_aceite(caja, notas=request.POST.get("notas", ""), filtros_cambiados=False)
    messages.success(request, "Cambio de aceite de caja registrado. Contador de km reseteado.")
    return redirect("vehiculo_aceite", vehiculo_pk=vehiculo.pk)
