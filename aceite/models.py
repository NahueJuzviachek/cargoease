# aceite/models.py
from decimal import Decimal
from django.db import models
from django.utils import timezone

class TipoAceite(models.TextChoices):
    MOTOR = "motor", "Motor"
    CAJA = "caja", "Caja"

class Aceite(models.Model):
    vehiculo = models.ForeignKey(
        "vehiculos.Vehiculo",
        on_delete=models.CASCADE,
        related_name="aceites",
        db_index=True,
    )

    tipo = models.CharField(max_length=20, choices=TipoAceite.choices, db_index=True)
    km_acumulados = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    # La vida útil la fijamos por tipo (Motor 30000, Caja 100000) al crear/cambiar
    vida_util_km = models.PositiveIntegerField(default=30000)
    ciclos = models.PositiveIntegerField(default=0)
    fecha_instalacion = models.DateField(default=timezone.now)

    class Meta:
        db_table = "tablaAceite"
        ordering = ["vehiculo_id", "tipo", "-fecha_instalacion"]

    def __str__(self):
        return f"{self.vehiculo} – {self.get_tipo_display()} (ciclo {self.ciclos})"

    @property
    def porcentaje_uso(self) -> float:
        try:
            if self.vida_util_km <= 0:
                return 0.0
            return float((self.km_acumulados / Decimal(self.vida_util_km)) * 100)
        except Exception:
            return 0.0


class AceiteCambio(models.Model):
    aceite = models.ForeignKey(Aceite, on_delete=models.CASCADE, related_name="historial")
    fecha = models.DateTimeField(default=timezone.now)
    km_acumulados_al_cambio = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    filtros_cambiados = models.BooleanField(default=False, help_text="Solo aplica a motor.")

    class Meta:
        db_table = "tablaAceiteCambio"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Cambio {self.aceite.get_tipo_display()} – {self.fecha:%d/%m/%Y}"
