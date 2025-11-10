# clientes/models.py
from django.db import models
from ubicaciones.models import Pais, Provincia, Localidad

class Cliente(models.Model):
    """
    Representa un cliente con datos de contacto y ubicación.
    Las relaciones a pais/provincia/localidad son opcionales pero protegidas.
    """
    nombre = models.CharField(max_length=50)
    correo = models.EmailField("Correo", max_length=254, unique=True)

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

    class Meta:
        db_table = 'tablaClientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        """
        Representación legible del cliente.
        """
        return f"{self.nombre} - {self.correo}"
