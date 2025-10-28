from django import forms
from datetime import date
import re
from .models import Vehiculo

# ---------------- Expresiones regulares para patentes ----------------
PATENTE_NUEVA = re.compile(r"^[A-Z]{2}\d{3}[A-Z]{2}$")  # Ej: AA123BB
PATENTE_VIEJA = re.compile(r"^[A-Z]{3}\d{3}$")          # Ej: ABC123


class VehiculoForm(forms.ModelForm):
    """
    Formulario para crear o editar vehículos.
    Incluye validación de año, cantidad de ejes y formatos de dominio.
    """

    class Meta:
        model = Vehiculo
        fields = [
            "marca",
            "modelo",
            "anio_fabricacion",
            "dominio",
            "dominio_remolque",
            "ejes",
        ]

        # ---------------- Widgets ----------------
        widgets = {
            "marca": forms.TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "modelo": forms.TextInput(attrs={"class": "form-control", "placeholder": ""}),
            "anio_fabricacion": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: 2018",
                "min": 1950
            }),
            "dominio": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "AA123BB o ABC123",
                "style": "text-transform:uppercase"
            }),
            "dominio_remolque": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "AA123BB o ABC123",
                "style": "text-transform:uppercase"
            }),
            "ejes": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Ej: 2, 3, 4...",
                "min": 1,
                "step": 1
            }),
        }

        # ---------------- Etiquetas de campos ----------------
        labels = {
            "marca": "Marca",
            "modelo": "Modelo",
            "anio_fabricacion": "Año de fabricación",
            "dominio": "Dominio",
            "dominio_remolque": "Dominio remolque (opcional)",
            "ejes": "Cantidad de ejes",
        }

    # ---------------- Validaciones individuales ----------------
    def clean_anio_fabricacion(self):
        """
        Valida que el año de fabricación esté entre 1950 y el año actual.
        """
        anio = self.cleaned_data.get("anio_fabricacion")
        current = date.today().year
        if anio is None:
            raise forms.ValidationError("Indicá el año de fabricación.")
        if anio < 1950 or anio > current:
            raise forms.ValidationError(f"El año debe estar entre 1950 y {current}.")
        return anio

    def _validar_patente(self, valor, campo):
        """
        Valida que el dominio siga los formatos AA123BB o ABC123.
        """
        if not (PATENTE_NUEVA.match(valor) or PATENTE_VIEJA.match(valor)):
            raise forms.ValidationError(f"Formato inválido para {campo}. Usá AA123BB o ABC123.")

    def clean_dominio(self):
        """
        Convierte a mayúsculas y valida el dominio principal.
        """
        dom = (self.cleaned_data.get("dominio") or "").strip().upper()
        self._validar_patente(dom, "dominio")
        return dom

    def clean_dominio_remolque(self):
        """
        Convierte a mayúsculas y valida el dominio del remolque, si se ingresa.
        """
        domr = self.cleaned_data.get("dominio_remolque")
        if not domr:
            return domr
        domr = domr.strip().upper()
        self._validar_patente(domr, "dominio remolque")
        return domr

    def clean_ejes(self):
        """
        Valida que la cantidad de ejes sea un número positivo mayor o igual a 1.
        """
        ejes = self.cleaned_data.get("ejes")
        if ejes is None:
            raise forms.ValidationError("Indicá la cantidad de ejes.")
        if ejes < 1:
            raise forms.ValidationError("La cantidad de ejes debe ser al menos 1.")
        return ejes
