# aceite/views.py
from decimal import Decimal
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone

from vehiculos.models import Vehiculo
from .models import AceiteMotor, AceiteCaja, ACEITE_MOTOR_MAX_KM, ACEITE_CAJA_MAX_KM
from .services import (
    asegurar_ciclo_motor, asegurar_ciclo_caja,
    recalc_km_motor, recalc_km_caja,
)

def aceite_dashboard(request, vehiculo_pk):
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_pk)

    # asegura ciclos y PERSISTE km actuales
    asegurar_ciclo_motor(vehiculo)
    asegurar_ciclo_caja(vehiculo)
    ciclo_motor = recalc_km_motor(vehiculo)
    ciclo_caja  = recalc_km_caja(vehiculo)

    usados_motor = min(Decimal(ciclo_motor.km), Decimal(ACEITE_MOTOR_MAX_KM))
    usados_caja  = min(Decimal(ciclo_caja.km),  Decimal(ACEITE_CAJA_MAX_KM))

    ctx = {
        "vehiculo": vehiculo,
        "ultimo_motor": ciclo_motor,
        "ultimo_caja":  ciclo_caja,
        "usados_motor": float(usados_motor),
        "usados_caja":  float(usados_caja),
        "restantes_motor": float(Decimal(ACEITE_MOTOR_MAX_KM) - usados_motor),
        "restantes_caja":  float(Decimal(ACEITE_CAJA_MAX_KM)  - usados_caja),
        "max_motor": ACEITE_MOTOR_MAX_KM,
        "max_caja":  ACEITE_CAJA_MAX_KM,
    }
    return render(request, "aceite/aceite_dashboard.html", ctx)


def cambiar_aceite_motor(request, vehiculo_pk):
    if request.method != "POST":
        return redirect(reverse("vehiculo_aceite", args=[vehiculo_pk]))
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_pk)

    # cerrar ciclo actual persistiendo km
    recalc_km_motor(vehiculo)

    # nuevo ciclo con km=0
    filtros_flag = request.POST.get("filtros") == "on"
    AceiteMotor.objects.create(
        vehiculo=vehiculo,
        fecha=timezone.localdate(),
        filtros=filtros_flag,
        km=Decimal("0"),
    )
    messages.success(request, "Cambio de aceite de MOTOR registrado. Contador reiniciado.")
    return redirect(reverse("vehiculo_aceite", args=[vehiculo.pk]))


def cambiar_aceite_caja(request, vehiculo_pk):
    if request.method != "POST":
        return redirect(reverse("vehiculo_aceite", args=[vehiculo_pk]))
    vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_pk)

    recalc_km_caja(vehiculo)
    AceiteCaja.objects.create(
        vehiculo=vehiculo,
        fecha=timezone.localdate(),
        km=Decimal("0"),
    )
    messages.success(request, "Cambio de aceite de CAJA registrado. Contador reiniciado.")
    return redirect(reverse("vehiculo_aceite", args=[vehiculo.pk]))
