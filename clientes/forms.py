from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    # Mostramos "Provincia" pero seguimos guardando en el campo `localidad` (CharField)
    localidad = forms.ChoiceField(
        choices=(),  # las cargamos dinámicamente en __init__
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Provincia",
        required=True,
    )

    class Meta:
        model = Cliente
        fields = ["nombre", "correo", "localidad", "divisa"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre"}),
            "correo": forms.EmailInput(attrs={"class": "form-control", "placeholder": "correo@ejemplo.com"}),
            "divisa": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "nombre": "Nombre",
            "correo": "Correo",
            # El label de localidad lo definimos arriba como "Provincia"
            "divisa": "Divisa",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Import local para evitar ciclos
        from ubicaciones.models import Provincia

        provincias = (
            Provincia.objects
            .select_related("pais")
            .order_by("nombre")
        )
        # Guardamos el nombre de la provincia en el CharField `localidad`,
        # y mostramos "Provincia (País)" en la UI
        self.fields["localidad"].choices = [("", "— Seleccionar provincia —")] + [
            (p.nombre, f"{p.nombre} ({p.pais.nombre})") for p in provincias
        ]

    
    