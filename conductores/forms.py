from django import forms
from vehiculos.models import Vehiculo
from .models import Conductor

class VehiculoChoiceField(forms.ModelChoiceField):
    # Muestra solo "Marca Modelo" en el desplegable
    def label_from_instance(self, obj: Vehiculo) -> str:
        return f"{obj.marca} {obj.modelo}"

class ConductorForm(forms.ModelForm):
    vehiculo = VehiculoChoiceField(
        queryset=Vehiculo.objects.all().order_by("marca", "modelo"),
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Conductor
        fields = ["nombreApellido", "dni", "vehiculo", "dominio"]
        widgets = {
            "nombreApellido": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre y Apellido"}),
            "dni": forms.TextInput(attrs={"class": "form-control", "placeholder": "DNI"}),
            # dominio como solo lectura en UI; igualmente lo forzamos del lado servidor en clean()
            "dominio": forms.TextInput(attrs={"class": "form-control", "readonly": "readonly", "placeholder": "Se completa según el vehículo"}),
        }
        labels = {
            "nombreApellido": "Nombre y Apellido",
            "dni": "DNI",
            "vehiculo": "Vehículo (Marca + Modelo)",
            "dominio": "Dominio",
        }

    def clean(self):
        cleaned = super().clean()
        vehiculo = cleaned.get("vehiculo")
        if vehiculo:
            # forzamos que dominio SIEMPRE coincida con el del vehículo seleccionado
            cleaned["dominio"] = vehiculo.dominio
        return cleaned
