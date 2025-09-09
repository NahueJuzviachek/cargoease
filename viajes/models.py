from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Divisa(models.Model):
    nombre = models.CharField(max_length=50)
    codigo = models.CharField(max_length=10, unique=True)
    simbolo = models.CharField(max_length=5, blank=True)

    class Meta:
        db_table = 'tablaDivias'
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

    # Fecha del viaje
    fecha = models.DateField(db_index=True, help_text="Fecha del viaje.")

    # Ubicaciones (app 'ubicaciones')
    salida = models.ForeignKey(
        "ubicaciones.Localidad", on_delete=models.PROTECT,
        related_name="viajes_salida", db_index=True
    )
    destino = models.ForeignKey(
        "ubicaciones.Localidad", on_delete=models.PROTECT,
        related_name="viajes_destino", db_index=True
    )
    # Km Recorridos por el vehiculo
    distancia = models.DecimalField(
        max_digits=8, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))]
    )
    # Economia
    valor_flete = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))]
    )
    divisa = models.ForeignKey(
        "viajes.Divisa", on_delete=models.PROTECT, related_name="viajes"
    )
    viaticos = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
        help_text="Porcentaje de viáticos (0–100)."
    )
    gasto = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0"))]
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
            models.Index(fields=["salida"]),
            models.Index(fields=["destino"]),
            models.Index(fields=["fecha"]),   # Indice por fecha
        ]
        ordering = ["-fecha", "-creado_en"]  # Primero por fecha más reciente

    def __str__(self):
        return f"Viaje #{self.pk} - {self.vehiculo} ({self.salida} → {self.destino}) {self.fecha}"


    # Calcular la ganancia del viaje antes de guardar
    def calcular_ganancia(self):
        gasto = self.gasto or Decimal("0")
        viaticos_monto = (self.valor_flete * (self.viaticos / Decimal("100")))
        ganancia = self.valor_flete - viaticos_monto - gasto
        return ganancia if ganancia >= 0 else Decimal("0")

    def save(self, *args, **kwargs):
        if self.valor_flete is not None and self.viaticos is not None:
            self.ganancia_total = self.calcular_ganancia()
        super().save(*args, **kwargs)
