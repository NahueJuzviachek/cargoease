# neumaticos/forms.py
from django import forms

class CambiarNeumaticosForm(forms.Form):
    neumaticos_ids = forms.CharField()
    destino = forms.CharField()
    eje_destino = forms.IntegerField(required=False, min_value=1)
    posicion_destino = forms.IntegerField(required=False, min_value=1)

    def clean_neumaticos_ids(self):
        raw = (self.cleaned_data["neumaticos_ids"] or "").strip()
        ids = [i for i in raw.split(",") if i.isdigit()]
        if not ids:
            raise forms.ValidationError("No seleccionaste neumáticos válidos.")
        return [int(i) for i in ids]
