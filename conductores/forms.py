from django import forms
from .models import Conductor
from vehiculos.models import Vehiculo
import re

# Expresiones regulares para validar patentes
PATENTE_NUEVA = re.compile(r"^[A-Z]{2}\d{3}[A-Z]{2}$")  # Ej: AA123BB
PATENTE_VIEJA = re.compile(r"^[A-Z]{3}\d{3}$")          # Ej: ABC123

class VehiculoChoiceField(forms.ModelChoiceField):
    """
    Muestra solo 'Marca Modelo' en el select de vehículos.
    """
    def label_from_instance(self, obj):
        return f"{obj.marca} {obj.modelo}"

class ConductorForm(forms.ModelForm):
    """
    Formulario para crear o editar conductores.
    Toma el dominio automáticamente desde el vehículo seleccionado.
    """
    vehiculo = VehiculoChoiceField(
        queryset=Vehiculo.objects.all().order_by("marca", "modelo"),
        label="Vehículo",
        widget=forms.Select(attrs={"class": "form-select"}),
        required=True,
    )

    class Meta:
        model = Conductor
        fields = ["nombreApellido", "dni", "vehiculo", "dominio"]
        widgets = {
            "nombreApellido": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre y Apellido"}),
            "dni": forms.TextInput(attrs={"class": "form-control", "placeholder": "Solo números"}),
            "dominio": forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),  # Se rellena automáticamente
        }

    def clean_dni(self):
        """
        Valida que el DNI contenga solo números y tenga longitud correcta.
        """
        dni = (self.cleaned_data.get("dni") or "").strip()
        if not dni.isdigit():
            raise forms.ValidationError("El DNI debe contener solo números.")
        if not (7 <= len(dni) <= 8):
            raise forms.ValidationError("El DNI debe tener 7 u 8 dígitos.")
        return dni

    def clean(self):
        """
        Valida la patente del vehículo y asigna el dominio al conductor.
        """
        cleaned = super().clean()
        vehiculo_obj = cleaned.get("vehiculo")

        if vehiculo_obj:
            cleaned["dominio"] = vehiculo_obj.dominio
            if not (PATENTE_NUEVA.match(vehiculo_obj.dominio) or PATENTE_VIEJA.match(vehiculo_obj.dominio)):
                raise forms.ValidationError("El dominio del vehículo seleccionado no tiene un formato válido.")
        return cleaned
