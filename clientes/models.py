from django.db import models

# Create your models here.


class Cliente(models.Model):  #tabla clientes
    nombre = models.CharField(max_length=50)
    localidad= models.CharField(max_length=50, default="Indicar")
    divisa= models.CharField(max_length=50, default="peso")
    
    class Meta:  #nombre de la tabla
        db_table='tablaClientes'
        verbose_name= 'Cliente'
        verbose_name_plural= 'Cliente'
    

    
