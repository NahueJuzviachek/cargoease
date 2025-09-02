from django import forms
from .models import Cliente
from ubicaciones.models import Pais, Provincia, Localidad


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["nombre", "correo", "pais", "provincia", "localidad"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre"}
            ),
            "correo": forms.EmailInput(
                attrs={"class": "form-control", "placeholder": "correo@ejemplo.com"}
            ),
            "pais": forms.Select(attrs={"class": "form-select"}),
            "provincia": forms.Select(attrs={"class": "form-select"}),
            "localidad": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "nombre": "Nombre",
            "correo": "Correo",
            "pais": "País",
            "provincia": "Provincia / Estado",
            "localidad": "Localidad",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Siempre cargar países
        self.fields["pais"].queryset = Pais.objects.all().order_by("nombre")

        # Provincias dinámicas según país
        if "pais" in self.data:
            try:
                pais_id = int(self.data.get("pais"))
                self.fields["provincia"].queryset = Provincia.objects.filter(pais_id=pais_id).order_by("nombre")
            except (TypeError, ValueError):
                self.fields["provincia"].queryset = Provincia.objects.none()
        elif self.instance.pk:
            self.fields["provincia"].queryset = Provincia.objects.filter(pais=self.instance.pais).order_by("nombre")
        else:
            self.fields["provincia"].queryset = Provincia.objects.none()

        # Localidades dinámicas según provincia
        if "provincia" in self.data:
            try:
                prov_id = int(self.data.get("provincia"))
                self.fields["localidad"].queryset = Localidad.objects.filter(provincia_id=prov_id).order_by("nombre")
            except (TypeError, ValueError):
                self.fields["localidad"].queryset = Localidad.objects.none()
        elif self.instance.pk:
            self.fields["localidad"].queryset = Localidad.objects.filter(provincia=self.instance.provincia).order_by("nombre")
        else:
            self.fields["localidad"].queryset = Localidad.objects.none()
