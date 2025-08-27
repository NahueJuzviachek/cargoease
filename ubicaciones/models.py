from django.db import models

class Pais(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo_iso = models.CharField(max_length=3, unique=True)  # Ej: ARG, BRA

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.codigo_iso})"


class Provincia(models.Model):
    # usamos id automático, y guardamos el código oficial en `codigo`
    codigo = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    nombre = models.CharField(max_length=150)
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name="provincias")

    class Meta:
        unique_together = ('pais', 'nombre')
        ordering = ['pais', 'nombre']

    def __str__(self):
        return f"{self.nombre} - {self.pais.codigo_iso}"


class Municipio(models.Model):
    codigo = models.CharField(max_length=30, null=True, blank=True, db_index=True)  # IBGE / INDEC code
    nombre = models.CharField(max_length=200)
    provincia = models.ForeignKey(Provincia, on_delete=models.CASCADE, related_name="municipios")

    class Meta:
        unique_together = ('provincia', 'nombre')
        ordering = ['provincia', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.provincia.nombre} - {self.provincia.pais.codigo_iso})"