from django.db import models

# Create your models here.

class Cliente(models.Model):  # tabla clientes
    # Choices para el <select> de divisa
    DIVISA_PESO  = "Peso"
    DIVISA_REAL  = "Real"
    DIVISA_DOLAR = "Dolar"
    DIVISAS = [
        (DIVISA_PESO, "Peso"),
        (DIVISA_REAL, "Real"),
        (DIVISA_DOLAR, "Dolar"),
    ]

    nombre = models.CharField(max_length=50)
    correo = models.EmailField("Correo", max_length=254, unique=True)
    localidad = models.CharField(max_length=50, default="Indicar")
    divisa = models.CharField(max_length=50, choices=DIVISAS, default=DIVISA_PESO)

    class Meta:  # nombre de la tabla
        db_table = 'tablaClientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f"{self.nombre} - {self.correo}"

    
