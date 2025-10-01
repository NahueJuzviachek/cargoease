# aceite/views.py
from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from vehiculos.models import Vehiculo
from .models import Aceite, TipoAceite
from .services import cambiar_aceite, recalc_km_aceite_para_vehiculo, MAX_MOTOR, MAX_CAJA


def confirmar_cambio_motor(request, vehiculo_pk: int):
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_pk)
    aceite = _ensure_aceite(vehiculo, TipoAceite.MOTOR)
    return render(request, "aceite/confirm.html", {"vehiculo": vehiculo, "aceite": aceite})

def confirmar_cambio_caja(request, vehiculo_pk: int):
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_pk)
    aceite = _ensure_aceite(vehiculo, TipoAceite.CAJA)
    return render(request, "aceite/confirm.html", {"vehiculo": vehiculo, "aceite": aceite})

def _suma_km_viajes(vehiculo):
    from viajes.models import Viaje
    total = Viaje.objects.filter(vehiculo=vehiculo).aggregate(s=Sum("distancia"))["s"]
    return Decimal(total or 0)

def _ensure_aceite(vehiculo, tipo: str) -> Aceite:
    aceite = Aceite.objects.filter(vehiculo=vehiculo, tipo=tipo).first()
    if not aceite:
        vida_default = MAX_MOTOR if tipo == TipoAceite.MOTOR else MAX_CAJA
        aceite = Aceite.objects.create(
            vehiculo=vehiculo,
            tipo=tipo,
            km_acumulados=0,
            vida_util_km=vida_default,
            # fecha_instalacion se setea por default=timezone.now
        )
    return aceite

def aceite_dashboard(request, vehiculo_pk: int):
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_pk)
    motor = _ensure_aceite(vehiculo, TipoAceite.MOTOR)
    caja = _ensure_aceite(vehiculo, TipoAceite.CAJA)

    recalc_km_aceite_para_vehiculo(vehiculo)
    motor.refresh_from_db(); caja.refresh_from_db()

    km_motor = float(motor.km_acumulados or 0)
    km_caja  = float(caja.km_acumulados or 0)
    max_motor = float(motor.vida_util_km or MAX_MOTOR)
    max_caja  = float(caja.vida_util_km or MAX_CAJA)

    pct_motor_cap = min(100.0, (km_motor / max_motor) * 100.0) if max_motor else 0.0
    pct_caja_cap  = min(100.0, (km_caja  / max_caja)  * 100.0) if max_caja  else 0.0

    ctx = {
        "vehiculo": vehiculo,
        "motor": motor, "caja": caja,
        "km_motor": motor.km_acumulados, "km_caja": caja.km_acumulados,
        "max_motor": int(max_motor), "max_caja": int(max_caja),
        "pct_motor_cap": pct_motor_cap, "pct_caja_cap": pct_caja_cap,
    }
    return render(request, "aceite/aceite_panel.html", ctx)

@require_POST
def cambiar_aceite_motor(request, vehiculo_pk: int):
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_pk)
    motor = _ensure_aceite(vehiculo, TipoAceite.MOTOR)
    filtros = request.POST.get("filtros_cambiados") == "on"
    cambiar_aceite(motor, filtros_cambiados=filtros)
    messages.success(request, "Cambio de aceite de motor registrado.")
    return redirect("vehiculo_aceite", vehiculo_pk=vehiculo.pk)

@require_POST
def cambiar_aceite_caja(request, vehiculo_pk: int):
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_pk)
    caja = _ensure_aceite(vehiculo, TipoAceite.CAJA)
    cambiar_aceite(caja, filtros_cambiados=False)
    messages.success(request, "Cambio de aceite de caja registrado.")
    return redirect("vehiculo_aceite", vehiculo_pk=vehiculo.pk)

