from django import forms

class formularioSoporte(forms.Form):
    
    tema=forms.CharField(label="Sobre", required=True)
    contenido=forms.CharField(label="Contenido", required=True, widget=forms.Textarea)