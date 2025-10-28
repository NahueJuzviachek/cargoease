from django.db import models
from vehiculos.models import Vehiculo

class Conductor(models.Model):
    """
    Modelo que representa un conductor asignado a un vehículo.
    """
    nombreApellido = models.CharField("Nombre y Apellido", max_length=100)
    dni = models.CharField("DNI", max_length=10, unique=True)  # Documento único
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name="conductores",
        verbose_name="Vehículo",
    )
    dominio = models.CharField(
        "Dominio",
        max_length=10,
        unique=True,
        help_text="Ej: AA123BB o ABC123",
    )

    class Meta:
        db_table = "tablaConductores"
        verbose_name = "Conductor"
        verbose_name_plural = "Conductores"
        ordering = ["id"]

    def __str__(self):
        """
        Representación legible: Nombre y DNI.
        """
        return f"{self.nombreApellido} ({self.dni})"
