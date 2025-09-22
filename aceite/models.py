# aceite/models.py
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

ACEITE_MOTOR_MAX_KM = 50000
ACEITE_CAJA_MAX_KM = 32000


class AceiteMotor(models.Model):
    vehiculo = models.ForeignKey("vehiculos.Vehiculo", on_delete=models.CASCADE, related_name="aceite_motor")
    # ⬇️ km acumulados del ciclo actual (persistidos)
    km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        default=Decimal("0"),
        help_text="Km acumulados desde el último cambio de aceite de motor."
    )
    filtros = models.BooleanField(default=False, help_text="¿Se cambiaron filtros en este cambio?")
    fecha = models.DateField(db_index=True)

    class Meta:
        db_table = "tablaAceiteMotor"
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return f"Motor {self.vehiculo} - {self.fecha} ({self.km} km)"


class AceiteCaja(models.Model):
    vehiculo = models.ForeignKey("vehiculos.Vehiculo", on_delete=models.CASCADE, related_name="aceite_caja")
    # ⬇️ km acumulados del ciclo actual (persistidos)
    km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        default=Decimal("0"),
        help_text="Km acumulados desde el último cambio de aceite de caja."
    )
    fecha = models.DateField(db_index=True)

    class Meta:
        db_table = "tablaAceiteCaja"
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return f"Caja {self.vehiculo} - {self.fecha} ({self.km} km)"
