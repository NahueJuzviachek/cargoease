from django.db import models

# Create your models here.

class Divisa(models.Model):
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

class Lugares(models.Model):
    nombre = models.CharField(max_length=50)

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    lugar = models.ForeignKey(Lugares, on_delete=models.PROTECT)
    divisa = models.ForeignKey(Divisa, on_delete=models.PROTECT)

    def __str__(self):
        return self.nombre
    
