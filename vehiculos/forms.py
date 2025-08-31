from django import forms
from .models import Vehiculo
from datetime import date
import re

PATENTE_VIEJA = re.compile(r"^[A-Z]{3}\d{3}$")     # ABC123
PATENTE_NUEVA = re.compile(r"^[A-Z]{2}\d{3}[A-Z]{2}$")  # AB123CD

class VehiculoForm(forms.ModelForm):
    class Meta:
        model = Vehiculo
        fields = ["marca", "modelo", "anio_fabricacion", "dominio", "dominio_remolque"]

        help_texts = {
            "marca": "Ej.: Mercedes-Benz, Scania, Iveco…",
            "modelo": "Ej.: Actros 2545, G 410, Tector…",
            "anio_fabricacion": f"Ingrese un año entre 1900 y {date.today().year}.",
            "dominio": "Formatos válidos AR: ABC123 o AB123CD (se normaliza a MAYÚSCULAS).",
            "dominio_remolque": "Opcional. Mismo formato que dominio principal.",
        }

        widgets = {
            "marca": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej.: Scania",
            }),
            "modelo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej.: G 410",
            }),
            "anio_fabricacion": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1900,
                "max": date.today().year,
                "placeholder": "Ej.: 2019",
            }),
            "dominio": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej.: AB123CD o ABC123",
                # Validación de navegador (client-side)
                "pattern": r"[A-Za-z]{3}\d{3}|[A-Za-z]{2}\d{3}[A-Za-z]{2}",
                "title": "Use ABC123 o AB123CD (u otro formato de su país).",
                "style": "text-transform:uppercase",
            }),
            "dominio_remolque": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Opcional: AB123CD o ABC123",
                "pattern": r"[A-Za-z]{3}\d{3}|[A-Za-z]{2}\d{3}[A-Za-z]{2}",
                "title": "Use ABC123 o AB123CD (u otro formato de su país).",
                "style": "text-transform:uppercase",
            }),
        }

    # Normalizo y valido dominios en server-side
    def _normalizar_patente(self, v: str) -> str:
        v = (v or "").strip().upper().replace(" ", "")
        return v

    def clean_dominio(self):
        v = self._normalizar_patente(self.cleaned_data.get("dominio"))
        if not v:
            raise forms.ValidationError("El dominio es obligatorio.")
        # Permitimos otros países, pero si es AR, validamos patrones comunes
        if not (PATENTE_VIEJA.match(v) or PATENTE_NUEVA.match(v)):
            # No rechazamos formatos extranjeros; sólo advertimos si querés:
            # raise forms.ValidationError("Formato de dominio no reconocido (ABC123 o AB123CD).")
            pass
        return v

    def clean_dominio_remolque(self):
        v = self.cleaned_data.get("dominio_remolque")
        if not v:
            return v
        v = self._normalizar_patente(v)
        # Igual criterio que dominio
        return v
