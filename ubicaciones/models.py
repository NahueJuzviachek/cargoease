from django.db import models

class Pais(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Provincia(models.Model):
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name="provincias")
    nombre = models.CharField(max_length=100)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        verbose_name = "Provincia"
        verbose_name_plural = "Provincias"
        ordering = ["nombre"]
        unique_together = ("pais", "nombre")

    def __str__(self):
        return f"{self.nombre} ({self.pais})"


class Localidad(models.Model):
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name="localidades")
    nombre = models.CharField(max_length=100)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        verbose_name = "Localidad"
        verbose_name_plural = "Localidades"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.provincia})"
