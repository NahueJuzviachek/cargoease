from django.db import models
from vehiculos.models import Vehiculo

class Conductor(models.Model):
    nombreApellido = models.CharField("Nombre y Apellido", max_length=120)
    dni = models.CharField("DNI", max_length=15, unique=True)

    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.PROTECT,
        related_name="conductores",
        verbose_name="Vehículo",
        null=True, blank=True,          # ← TEMPORAL (importante)
    )

    dominio = models.CharField("Dominio", max_length=10)

    class Meta:
        verbose_name = "Conductor"
        verbose_name_plural = "Conductores"
        ordering = ["id"]

    def __str__(self):
        v = self.vehiculo
        vm = f"{v.marca} {v.modelo} ({v.dominio})" if v else "sin vehículo"
        return f"{self.nombreApellido} - {vm}"


