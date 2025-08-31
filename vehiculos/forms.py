from django import forms
from .models import Vehiculo
import re
from datetime import date

PATENTE_NUEVA = re.compile(r"^[A-Z]{2}\d{3}[A-Z]{2}$")  # AA123BB
PATENTE_VIEJA = re.compile(r"^[A-Z]{3}\d{3}$")          # ABC123

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ["marca", "modelo", "anio", "dominio", "dominio_remolque"]  # ← agregamos anio acá
        widgets = {
            "marca": forms.TextInput(attrs={"class": "form-control", "placeholder": "Marca"}),
            "modelo": forms.TextInput(attrs={"class": "form-control", "placeholder": "Modelo"}),

            "anio": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Año",
                "min": 1900,
                "max": date.today().year + 1
            }),

            "dominio": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "AA123BB o ABC123",
                "style": "text-transform:uppercase"
            }),
            "dominio_remolque": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Opcional: AA123BB o ABC123",
                "style": "text-transform:uppercase"
            }),
        }
        labels = {
            "marca": "Marca",
            "modelo": "Modelo",
            "anio": "Año",
            "dominio": "Dominio",
            "dominio_remolque": "Dominio remolque (opcional)",
        }

    def _validar_patente(self, valor, campo):
        if not (PATENTE_NUEVA.match(valor) or PATENTE_VIEJA.match(valor)):
            raise forms.ValidationError(f"Formato inválido para {campo}. Use AA123BB o ABC123.")

    def clean_dominio(self):
        dom = (self.cleaned_data.get("dominio") or "").strip().upper()
        self._validar_patente(dom, "dominio")
        return dom

    def clean_dominio_remolque(self):
        domr = self.cleaned_data.get("dominio_remolque")
        if not domr:
            return domr
        domr = domr.strip().upper()
        self._validar_patente(domr, "dominio remolque")
        return domr

    def clean_anio(self):
        anio = self.cleaned_data.get("anio")
        año_max = date.today().year + 1
        if anio and not (1900 <= anio <= año_max):
            raise forms.ValidationError(f"El año debe estar entre 1900 y {año_max}.")
        return anio
