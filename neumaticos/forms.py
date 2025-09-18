# neumaticos/forms.py
from django import forms

CONDICION_CHOICES = [
    ("", "Dejar igual"),
    ("nuevo", "Nuevo"),
    ("recapado", "Recapado"),
    ("usado", "Usado"),
]

class CambiarNeumaticosForm(forms.Form):
    neumaticos_ids = forms.CharField()
    destino = forms.CharField()
    eje_destino = forms.IntegerField(required=False, min_value=1)
    posicion_destino = forms.IntegerField(required=False, min_value=1)
    tipo_condicion = forms.ChoiceField(choices=CONDICION_CHOICES, required=False)

    def clean_neumaticos_ids(self):
        raw = (self.cleaned_data["neumaticos_ids"] or "").strip()
        ids = [i for i in raw.split(",") if i.isdigit()]
        if not ids:
            raise forms.ValidationError("No seleccionaste neumáticos válidos.")
        return [int(i) for i in ids]

class ReubicarForm(forms.Form):
    neumaticos_ids_swap = forms.CharField()

    def clean_neumaticos_ids_swap(self):
        raw = (self.cleaned_data["neumaticos_ids_swap"] or "").strip()
        ids = [int(i) for i in raw.split(",") if i.isdigit()]
        ids = list(dict.fromkeys(ids))  # únicos y en orden
        if len(ids) != 2:
            raise forms.ValidationError("Debés seleccionar exactamente 2 neumáticos para reubicar.")
        return ids
