from django.db import models

class Vehiculo(models.Model):
    marca = models.CharField("Marca", max_length=60)
    modelo = models.CharField("Modelo", max_length=60)
    anio_fabricacion = models.PositiveSmallIntegerField("Año de fabricación")
    dominio = models.CharField("Dominio", max_length=10, unique=True, help_text="AA123BB o ABC123")
    dominio_remolque = models.CharField(
        "Dominio remolque",
        max_length=10,
        blank=True,
        null=True,
        unique=True,   # múltiples NULL permitidos; si se completa, debe ser único
        help_text="Opcional. AA123BB o ABC123"
    )

    class Meta:
        db_table = "tablaVehiculos"
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ["id"]

    def __str__(self):
        return f"{self.marca} {self.modelo} {self.anio_fabricacion} ({self.dominio})"

