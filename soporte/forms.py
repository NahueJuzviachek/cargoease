from django import forms

class SoporteForm(forms.Form):
    nombre = forms.CharField(
        label="Tu nombre",
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Escribí tu nombre",
        })
    )
    email = forms.EmailField(
        label="Tu correo",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "tu@correo.com",
        })
    )
    mensaje = forms.CharField(
        label="Mensaje",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 5,
            "placeholder": "Contanos el problema con el mayor detalle posible…",
        })
    )