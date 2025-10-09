from django import forms
from .models import TipoAceite

class CambioAceiteForm(forms.Form):
    filtros_cambiados = forms.BooleanField(
        required=False,
        label="¿Cambiar filtros?",
        help_text="Solo aplica al aceite de motor.",
    )

    def __init__(self, *args, **kwargs):
        self.aceite = kwargs.pop("aceite", None)
        super().__init__(*args, **kwargs)
        # Si no es motor, ocultamos el campo
        if not self.aceite or self.aceite.tipo != TipoAceite.MOTOR:
            self.fields["filtros_cambiados"].widget = forms.HiddenInput()
