from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date

def current_year():
    return date.today().year

class Vehiculo(models.Model):
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    anio_fabricacion = models.PositiveIntegerField(
        "Año de fabricación",
        validators=[MinValueValidator(1900), MaxValueValidator(current_year)]
    )
    dominio = models.CharField("Dominio", max_length=10, unique=True)
    dominio_remolque = models.CharField("Dominio del remolque", max_length=10, blank=True, null=True)

    class Meta:
        db_table = "tablaVehiculos"
        verbose_name = "Vehículo"
        verbose_name_plural = "Vehículos"
        ordering = ["id"]

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.anio_fabricacion}) - {self.dominio}"
