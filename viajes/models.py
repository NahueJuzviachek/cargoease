from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Divisa(models.Model):
    nombre = models.CharField(max_length=50)
    codigo = models.CharField(max_length=10, unique=True)
    simbolo = models.CharField(max_length=5, blank=True)

    class Meta:
        db_table = 'tablaDivisa'
        verbose_name = "Divisa"
        verbose_name_plural = "Divisas"
        ordering = ["codigo"]

    def __str__(self):
        return f"{self.codigo} ({self.nombre})"


class Viaje(models.Model):
    vehiculo = models.ForeignKey(
        "vehiculos.Vehiculo", on_delete=models.PROTECT,
        related_name="viajes", db_index=True
    )

    cliente = models.ForeignKey(
        "clientes.Cliente", on_delete=models.PROTECT,
        related_name="viajes", db_index=True,
        null=True, blank=True
    )

    fecha = models.DateField(db_index=True, help_text="Fecha del viaje.")

    # Ubicaciones
    salida = models.ForeignKey(
        "ubicaciones.Localidad", on_delete=models.PROTECT,
        related_name="viajes_salida", db_index=True
    )
    destino = models.ForeignKey(
        "ubicaciones.Localidad", on_delete=models.PROTECT,
        related_name="viajes_destino", db_index=True
    )

    # Km recorridos
    distancia = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))]
    )

    # Económicos
    valor_flete = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))]
    )
    divisa = models.ForeignKey(
        "viajes.Divisa", on_delete=models.PROTECT, related_name="viajes"
    )

    viaticos = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Monto de viáticos (no porcentaje)."
    )

    porcentaje_conductor = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
        help_text="Porcentaje del flete para el conductor (0–100)."
    )

    gasto = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Suma automática de todos los gastos extra del viaje."
    )

    ganancia_total = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Se calcula automáticamente al guardar."
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tablaViajes'
        verbose_name = "Viaje"
        verbose_name_plural = "Viajes"
        indexes = [
            models.Index(fields=["vehiculo"]),
            models.Index(fields=["cliente"]),
            models.Index(fields=["salida"]),
            models.Index(fields=["destino"]),
            models.Index(fields=["fecha"]),
        ]
        ordering = ["-fecha", "-creado_en"]

    def __str__(self):
        cli = f" - {self.cliente}" if self.cliente_id else ""
        return f"Viaje #{self.pk} - {self.vehiculo}{cli} ({self.salida} → {self.destino}) {self.fecha}"

    def monto_conductor(self) -> Decimal:
        flete = self.valor_flete or Decimal("0")
        pct = self.porcentaje_conductor or Decimal("0")
        return flete * (pct / Decimal("100"))

    def calcular_ganancia(self) -> Decimal:
        flete = self.valor_flete or Decimal("0")
        conductor = self.monto_conductor()
        viaticos_monto = self.viaticos or Decimal("0")
        gasto_monto = self.gasto or Decimal("0")
        ganancia = flete - conductor - viaticos_monto - gasto_monto
        return ganancia if ganancia >= 0 else Decimal("0")

    def save(self, *args, **kwargs):
        if self.valor_flete is not None and self.porcentaje_conductor is not None and self.viaticos is not None:
            self.ganancia_total = self.calcular_ganancia()
        super().save(*args, **kwargs)


class GastoExtra(models.Model):
    viaje = models.ForeignKey(
        Viaje,
        on_delete=models.CASCADE,
        related_name="gastos_extra",
        db_index=True,
    )
    fecha = models.DateField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    descripcion = models.CharField(max_length=255, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tablaGastosExtra"
        ordering = ["-fecha", "-id"]

    def __str__(self):
        return f"GastoExtra(viaje={self.viaje_id}, {self.fecha}, {self.monto})"


# --- Señales para mantener sincronizado gasto y ganancia_total ---
def _sumar_gastos_extra(viaje: Viaje) -> Decimal:
    total = viaje.gastos_extra.aggregate(s=Sum("monto"))["s"] or Decimal("0")
    return total


@receiver(post_save, sender=GastoExtra)
@receiver(post_delete, sender=GastoExtra)
def actualizar_gastos_y_ganancia(sender, instance: GastoExtra, **kwargs):
    viaje = instance.viaje
    total_extras = _sumar_gastos_extra(viaje)
    viaje.gasto = total_extras
    viaje.ganancia_total = viaje.calcular_ganancia()
    viaje.save(update_fields=["gasto", "ganancia_total", "actualizado_en"])
