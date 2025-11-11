# conductores/models.py
from django.db import models
from django.db.models import Q
from vehiculos.models import Vehiculo

class ActiveManager(models.Manager):
    """Manager que devuelve sólo registros activos (is_active=True)."""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class Conductor(models.Model):
    """
    Modelo que representa un conductor asignado a un vehículo.
    """
    nombreApellido = models.CharField("Nombre y Apellido", max_length=100)
    dni = models.CharField("DNI", max_length=10)  # removí `unique=True` para usar constraint condicional
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name="conductores",
        verbose_name="Vehículo",
    )
    dominio = models.CharField(
        "Dominio",
        max_length=10,
        help_text="Ej: AA123BB o ABC123",
    )

    # campo para baja lógica
    is_active = models.BooleanField("Activo", default=True, db_index=True)

    # managers
    objects = ActiveManager()      # por defecto devuelve sólo activos
    all_objects = models.Manager() # acceso completo cuando haga falta

    class Meta:
        db_table = "tablaConductores"
        verbose_name = "Conductor"
        verbose_name_plural = "Conductores"
        ordering = ["id"]
        # Opcional: restricciones únicas condicionadas a is_active.
        # Si querés mantener dni y dominio únicos sólo entre activos, descomenta las siguientes líneas
        constraints = [
            models.UniqueConstraint(fields=["dni"], condition=Q(is_active=True), name="unique_active_dni"),
            models.UniqueConstraint(fields=["dominio"], condition=Q(is_active=True), name="unique_active_dominio"),
        ]

    def __str__(self):
        """
        Representación legible: Nombre y DNI.
        """
        return f"{self.nombreApellido} ({self.dni})"

    def baja_logica(self):
        """Marca el registro como inactivo en vez de eliminarlo."""
        self.is_active = False
        self.save(update_fields=["is_active"])

    def alta(self):
        """Reactivar un conductor."""
        self.is_active = True
        self.save(update_fields=["is_active"])
