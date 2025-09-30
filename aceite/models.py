from decimal import Decimal
from django.db import models
from django.utils import timezone

class TipoAceite(models.TextChoices):
    MOTOR = "motor", "Motor"
    CAJA = "caja", "Caja"

class EstadoAceite(models.TextChoices):
    EN_USO = "en_uso", "En uso"
    CAMBIADO = "cambiado", "Cambiado"

class Aceite(models.Model):
    vehiculo = models.ForeignKey(
        "vehiculos.Vehiculo",
        on_delete=models.CASCADE,
        related_name="aceites",
        db_index=True
    )
    tipo = models.CharField(max_length=20, choices=TipoAceite.choices, db_index=True)

    # Snapshot al momento de instalar/cambiar:
    viajes_km_acumulados_al_instalar = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        help_text="Suma de km de viajes del vehículo al momento de instalar/cambiar."
    )

    # Estado y control
    km_acumulados = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    vida_util_km = models.PositiveIntegerField(
        default=15000, help_text="Intervalo recomendado de cambio (km)."
    )
    ciclos = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=20, choices=EstadoAceite.choices, default=EstadoAceite.EN_USO)

    fecha_instalacion = models.DateField(default=timezone.now)
    notas = models.TextField(blank=True)

    class Meta:
        db_table = "tablaAceite"
        verbose_name = "Aceite"
        verbose_name_plural = "Aceites"
        ordering = ["vehiculo_id", "tipo", "-fecha_instalacion"]

    def __str__(self):
        return f"{self.vehiculo} – {self.get_tipo_display()} (ciclo {self.ciclos})"

    @property
    def porcentaje_uso(self) -> float:
        if self.vida_util_km <= 0:
            return 0.0
        try:
            return float((self.km_acumulados / Decimal(self.vida_util_km)) * 100)
        except Exception:
            return 0.0


class AceiteCambio(models.Model):
    """
    Historial de cambios (reseteos). Guarda el km acumulado al cambiar.
    """
    aceite = models.ForeignKey(Aceite, on_delete=models.CASCADE, related_name="historial")
    fecha = models.DateTimeField(default=timezone.now)
    km_acumulados_al_cambio = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    notas = models.TextField(blank=True)
    filtros_cambiados = models.BooleanField(
        default=False,
        help_text="Solo aplica a cambios de aceite de motor."
    )
    
    class Meta:
        db_table = "tablaAceiteCambio"
        verbose_name = "Cambio de aceite"
        verbose_name_plural = "Cambios de aceite"
        ordering = ["-fecha"]

    def __str__(self):
        return f"Cambio {self.aceite.get_tipo_display()} de {self.aceite.vehiculo} – {self.fecha:%d/%m/%Y}"
