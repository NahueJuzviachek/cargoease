from django import forms 

class agregarCliente(forms.Form):
    
    nombre = forms.CharField(label="Nombre", required=True)
    lugar = forms.CharField(label="Lugar", required=True)
    divisa = forms.CharField(label="divisa", required=True)
    
    