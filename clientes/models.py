# clientes/models.py
from django.db import models
from django.db.models import Q
from ubicaciones.models import Pais, Provincia, Localidad

class ActiveManager(models.Manager):
    """Manager que devuelve sólo clientes activos (is_active=True)."""
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class Cliente(models.Model):
    """
    Representa un cliente con datos de contacto y ubicación.
    """
    nombre = models.CharField(max_length=50)
    correo = models.EmailField("Correo", max_length=254)  # removí unique=True para constraint condicional

    # Relaciona cliente con ubicación, evitando eliminación si se usan en clientes existentes
    pais = models.ForeignKey(
        Pais, on_delete=models.PROTECT, related_name="clientes", null=True, blank=True
    )
    provincia = models.ForeignKey(
        Provincia, on_delete=models.PROTECT, related_name="clientes", null=True, blank=True
    )
    localidad = models.ForeignKey(
        Localidad, on_delete=models.PROTECT, related_name="clientes", null=True, blank=True
    )

    # campo para baja lógica
    is_active = models.BooleanField("Activo", default=True, db_index=True)

    # managers
    objects = ActiveManager()      # por defecto devuelve sólo activos
    all_objects = models.Manager() # acceso completo cuando haga falta

    class Meta:
        db_table = 'tablaClientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        # Opcional: si querés que correo sea único solo entre activos:
        constraints = [
            models.UniqueConstraint(fields=["correo"], condition=Q(is_active=True), name="unique_active_correo"),
        ]

    def __str__(self):
        """
        Representación legible del cliente.
        """
        return f"{self.nombre} - {self.correo}"

    def baja_logica(self):
        """Marca el cliente como inactivo en vez de eliminarlo."""
        self.is_active = False
        self.save(update_fields=["is_active"])

    def alta(self):
        """Reactivar cliente."""
        self.is_active = True
        self.save(update_fields=["is_active"])
