from django import forms
from .models import AceiteMotor, AceiteCaja

class AceiteMotorForm(forms.ModelForm):
    class Meta:
        model = AceiteMotor
        fields = ["fecha", "km", "filtros"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "km": forms.NumberInput(attrs={"step": "0.01", "min": "0", "class": "form-control"}),
            "filtros": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {"fecha": "Fecha", "km": "Odómetro (opcional)", "filtros": "Cambiar filtros"}


class AceiteCajaForm(forms.ModelForm):
    class Meta:
        model = AceiteCaja
        fields = ["fecha", "km"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "km": forms.NumberInput(attrs={"step": "0.01", "min": "0", "class": "form-control"}),
        }
        labels = {"fecha": "Fecha", "km": "Odómetro (opcional)"}
