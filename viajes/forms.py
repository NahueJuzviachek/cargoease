from django import forms
from django.core.exceptions import ValidationError
from .models import Viaje, GastoExtra
from ubicaciones.models import Pais, Provincia, Localidad
from clientes.models import Cliente


class ViajeForm(forms.ModelForm):
    """
    Formulario para crear/editar viajes.
    Incluye campos de salida y destino con cascada país → provincia → localidad.
    """

    # -------- Salida (cascada) --------
    salida_pais = forms.ModelChoiceField(
        label="Salida - País",
        queryset=Pais.objects.all().order_by("nombre"),
        required=True,
        widget=forms.Select(attrs={"class": "form-select", "id": "id_salida_pais"})
    )
    salida_provincia = forms.ModelChoiceField(
        label="Salida - Provincia",
        queryset=Provincia.objects.none(),  # se llena dinámicamente
        required=True,
        widget=forms.Select(attrs={"class": "form-select", "id": "id_salida_provincia"})
    )
    salida_localidad = forms.ModelChoiceField(
        label="Salida - Localidad",
        queryset=Localidad.objects.none(),  # se llena dinámicamente
        required=True,
        widget=forms.Select(attrs={"class": "form-select", "id": "id_salida_localidad"})
    )

    # -------- Destino (cascada) --------
    destino_pais = forms.ModelChoiceField(
        label="Destino - País",
        queryset=Pais.objects.all().order_by("nombre"),
        required=True,
        widget=forms.Select(attrs={"class": "form-select", "id": "id_destino_pais"})
    )
    destino_provincia = forms.ModelChoiceField(
        label="Destino - Provincia",
        queryset=Provincia.objects.none(),  # se llena dinámicamente
        required=True,
        widget=forms.Select(attrs={"class": "form-select", "id": "id_destino_provincia"})
    )
    destino_localidad = forms.ModelChoiceField(
        label="Destino - Localidad",
        queryset=Localidad.objects.none(),  # se llena dinámicamente
        required=True,
        widget=forms.Select(attrs={"class": "form-select", "id": "id_destino_localidad"})
    )

    class Meta:
        model = Viaje
        # NOTA: 'gasto' ya no se edita desde el form: se calcula con GastoExtra
        fields = [
            "fecha",
            "cliente",
            "distancia",
            "divisa",
            "valor_flete",
            "porcentaje_conductor",
            "viaticos",
            # salida/destino se setean en save() desde *_localidad
        ]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "cliente": forms.Select(attrs={"class": "form-select"}),
            "distancia": forms.NumberInput(attrs={"step": "0.01", "min": "0", "class": "form-control"}),
            "divisa": forms.Select(attrs={"class": "form-select"}),
            "valor_flete": forms.NumberInput(attrs={"step": "0.01", "min": "0", "class": "form-control"}),
            "porcentaje_conductor": forms.NumberInput(attrs={"step": "0.01", "min": "0", "max": "100", "class": "form-control"}),
            "viaticos": forms.NumberInput(attrs={"step": "0.01", "min": "0", "class": "form-control"}),
        }
        labels = {
            "fecha": "Fecha",
            "cliente": "Cliente",
            "distancia": "Distancia (km)",
            "divisa": "Divisa",
            "valor_flete": "Valor del flete",
            "porcentaje_conductor": "Conductor (%)",
            "viaticos": "Viáticos (monto)",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ordenar clientes alfabéticamente
        self.fields["cliente"].queryset = Cliente.objects.all().order_by("nombre")

        # --- Precarga en edición ---
        if self.instance and self.instance.pk:
            # Salida
            if self.instance.salida_id:
                salida_loc = self.instance.salida
                salida_prov = salida_loc.provincia
                salida_pais = salida_prov.pais
                self.fields["salida_provincia"].queryset = Provincia.objects.filter(pais=salida_pais).order_by("nombre")
                self.fields["salida_localidad"].queryset = Localidad.objects.filter(provincia=salida_prov).order_by("nombre")
                self.initial["salida_pais"] = salida_pais
                self.initial["salida_provincia"] = salida_prov
                self.initial["salida_localidad"] = salida_loc

            # Destino
            if self.instance.destino_id:
                destino_loc = self.instance.destino
                destino_prov = destino_loc.provincia
                destino_pais = destino_prov.pais
                self.fields["destino_provincia"].queryset = Provincia.objects.filter(pais=destino_pais).order_by("nombre")
                self.fields["destino_localidad"].queryset = Localidad.objects.filter(provincia=destino_prov).order_by("nombre")
                self.initial["destino_pais"] = destino_pais
                self.initial["destino_provincia"] = destino_prov
                self.initial["destino_localidad"] = destino_loc
        else:
            # Alta: campos dependientes vacíos
            self.fields["salida_provincia"].queryset = Provincia.objects.none()
            self.fields["salida_localidad"].queryset = Localidad.objects.none()
            self.fields["destino_provincia"].queryset = Provincia.objects.none()
            self.fields["destino_localidad"].queryset = Localidad.objects.none()

        # Actualiza querysets si viene POST (para validar correctamente)
        data = self.data or None
        if data:
            sp = data.get("salida_pais")
            if sp:
                self.fields["salida_provincia"].queryset = Provincia.objects.filter(pais_id=sp).order_by("nombre")
            sprov = data.get("salida_provincia")
            if sprov:
                self.fields["salida_localidad"].queryset = Localidad.objects.filter(provincia_id=sprov).order_by("nombre")

            dp = data.get("destino_pais")
            if dp:
                self.fields["destino_provincia"].queryset = Provincia.objects.filter(pais_id=dp).order_by("nombre")
            dprov = data.get("destino_provincia")
            if dprov:
                self.fields["destino_localidad"].queryset = Localidad.objects.filter(provincia_id=dprov).order_by("nombre")

    def clean(self):
        """
        Validaciones de campos específicos:
        - cliente
        - salida_localidad
        - destino_localidad
        """
        cleaned = super().clean()

        if not cleaned.get("cliente"):
            self.add_error("cliente", "Debes seleccionar un cliente.")

        if not cleaned.get("salida_localidad"):
            self.add_error("salida_localidad", "Debes seleccionar la localidad de salida.")

        if not cleaned.get("destino_localidad"):
            self.add_error("destino_localidad", "Debes seleccionar la localidad de destino.")

        return cleaned

    def save(self, commit=True):
        """
        Sobrescribe save() para:
        - asignar FKs reales de salida/destino
        - el vehiculo se asigna desde la view
        """
        instance = super().save(commit=False)
        instance.salida = self.cleaned_data["salida_localidad"]
        instance.destino = self.cleaned_data["destino_localidad"]
        if commit:
            instance.save()
        return instance


class GastoExtraForm(forms.ModelForm):
    """
    Formulario para registrar gastos extras asociados a un viaje.
    """
    class Meta:
        model = GastoExtra
        fields = ["fecha", "monto", "descripcion"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "monto": forms.NumberInput(attrs={"step": "0.01", "min": "0", "class": "form-control"}),
            "descripcion": forms.Textarea(attrs={"rows": 2, "class": "form-control", "placeholder": "Peaje, comida, estacionamiento..."}),
        }
        labels = {
            "fecha": "Fecha",
            "monto": "Monto",
            "descripcion": "Descripción",
        }
