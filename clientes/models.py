from django.db import models
from ubicaciones.models import Pais, Provincia, Localidad  # 👈 importar de tu app

class Cliente(models.Model):
    nombre = models.CharField(max_length=50)
    correo = models.EmailField("Correo", max_length=254, unique=True)

    # Nuevos FK a ubicaciones
    pais = models.ForeignKey(Pais, on_delete=models.PROTECT, related_name="clientes", null=True, blank=True)
    provincia = models.ForeignKey(Provincia, on_delete=models.PROTECT, related_name="clientes", null=True, blank=True)
    localidad = models.ForeignKey(Localidad, on_delete=models.PROTECT, related_name="clientes", null=True, blank=True)

    class Meta:
        db_table = 'tablaClientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f"{self.nombre} - {self.correo}"

    
