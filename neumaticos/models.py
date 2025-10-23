# neumaticos/models.py
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from vehiculos.models import Vehiculo


class EstadoNeumatico(models.Model):
    idEstadoNeumatico = models.AutoField(primary_key=True, db_column="idEstadoNeumatico")
    descripcion = models.CharField("Descripción", max_length=50, unique=True)

    class Meta:
        db_table = "estadoNeumaticos"
        verbose_name = "Estado de neumático"
        verbose_name_plural = "Estados de neumático"
        ordering = ["idEstadoNeumatico"]

    def __str__(self):
        return self.descripcion


class TipoNeumatico(models.Model):
    idTipo = models.AutoField(primary_key=True, db_column="idTipo")
    descripcion = models.CharField("Descripción", max_length=50, unique=True)

    class Meta:
        db_table = "tipoNeumatico"
        verbose_name = "Tipo de neumático"
        verbose_name_plural = "Tipos de neumático"
        ordering = ["idTipo"]

    def __str__(self):
        return self.descripcion


class NeumaticoQuerySet(models.QuerySet):
    def vigentes(self):
        qs = self
        # filtrar por flags si existen
        if "activo" in [f.name for f in Neumatico._meta.fields]:
            qs = qs.filter(activo=True)
        if "eliminado" in [f.name for f in Neumatico._meta.fields]:
            qs = qs.filter(eliminado=False)
        if "fecha_baja" in [f.name for f in Neumatico._meta.fields]:
            qs = qs.filter(fecha_baja__isnull=True)
        # además, evitar estado ELIMINADO si alguien lo filtrara solo por estado
        try:
            qs = qs.exclude(estado__descripcion__iexact="ELIMINADO")
        except Exception:
            pass
        return qs


class NeumaticoManager(models.Manager):
    def get_queryset(self):
        return NeumaticoQuerySet(self.model, using=self._db)

    def vigentes(self):
        return self.get_queryset().vigentes()


class Neumatico(models.Model):
    idNeumatico = models.AutoField(primary_key=True, db_column="idNeumatico")

    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.SET_NULL,                 # mantenemos tu comportamiento actual
        related_name="neumaticos",
        db_column="idVehiculo",
        verbose_name="Vehículo",
        null=True,
        blank=True,
    )

    estado = models.ForeignKey(
        EstadoNeumatico,
        on_delete=models.PROTECT,
        db_column="idEstadoNeumatico",
        verbose_name="Estado",
    )

    tipo = models.ForeignKey(
        TipoNeumatico,
        on_delete=models.PROTECT,
        db_column="idTipoNeumatico",
        verbose_name="Tipo de neumático",
        null=True,
        blank=True,
    )

    nroNeumatico = models.PositiveIntegerField(
        "Nº de neumático",
        validators=[MinValueValidator(1)],
        help_text="Número interno/posición del neumático en el vehículo",
    )

    montado = models.BooleanField("¿Montado en vehículo?", default=False)

    km = models.PositiveIntegerField(
        "Kilómetros recorridos",
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Cantidad de km acumulados por el neumático",
    )

    # --- Soft delete flags (nuevos) ---
    activo = models.BooleanField(default=True)
    eliminado = models.BooleanField(default=False)
    fecha_baja = models.DateTimeField(null=True, blank=True)

    objects = NeumaticoManager()

    class Meta:
        db_table = "tablaNeumaticos"
        verbose_name = "Neumático"
        verbose_name_plural = "Neumáticos"
        ordering = ["idNeumatico"]
        constraints = [
            models.UniqueConstraint(
                fields=["vehiculo", "nroNeumatico"],
                name="uq_vehiculo_nro_neumatico",
            )
        ]

    def __str__(self):
        tipo = self.tipo.descripcion if self.tipo else "Sin tipo"
        if self.vehiculo:
            return f"Neumático #{self.nroNeumatico} - {self.vehiculo} ({tipo}, {self.km} km)"
        return f"Neumático #{self.nroNeumatico} (En almacén) - {tipo}, {self.km} km"

    # -------- Soft delete helpers --------
    def soft_delete(self, commit=True):
        estado_elim, _ = EstadoNeumatico.objects.get_or_create(descripcion="ELIMINADO")
        self.estado = estado_elim
        self.activo = False
        self.eliminado = True
        self.fecha_baja = timezone.now()
        if commit:
            self.save(update_fields=["estado", "activo", "eliminado", "fecha_baja"])

    def restore(self, estado_activo_desc="EN USO", commit=True):
        estado_activo, _ = EstadoNeumatico.objects.get_or_create(descripcion=estado_activo_desc)
        self.estado = estado_activo
        self.activo = True
        self.eliminado = False
        self.fecha_baja = None
        if commit:
            self.save(update_fields=["estado", "activo", "eliminado", "fecha_baja"])

    # opcional: si querés forzar que delete() sea soft
    def delete(self, using=None, keep_parents=False):
        self.soft_delete(commit=True)


class AlmacenNeumaticos(models.Model):
    idNeumatico = models.OneToOneField(
        Neumatico,
        on_delete=models.CASCADE,
        db_column="idNeumatico",
        primary_key=True,
        related_name="almacen",
        verbose_name="Neumático",
    )
    fecha_ingreso = models.DateField(auto_now_add=True, verbose_name="Fecha de ingreso")

    class Meta:
        db_table = "almacenNeumaticos"
        verbose_name = "Almacén de neumático"
        verbose_name_plural = "Almacén de neumáticos"
        ordering = ["fecha_ingreso"]

    def __str__(self):
        return f"Neumático {self.idNeumatico_id} en almacén desde {self.fecha_ingreso}"
