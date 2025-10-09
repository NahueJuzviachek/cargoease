from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import SoporteForm


def soporte_view(request):
    if request.method == "POST":
        form = SoporteForm(request.POST)
        if form.is_valid():
            ASUNTO_SOPORTE = "Informe de Problema"
            nombre = form.cleaned_data["nombre"]
            email_usuario = form.cleaned_data["email"]
            mensaje_usuario = form.cleaned_data["mensaje"]

            cuerpo = (
                "Nuevo reporte desde el Panel de Soporte (CargoEase)\n\n"
                f"Nombre: {nombre}\n"
                f"Email: {email_usuario}\n"
                f"Asunto: {ASUNTO_SOPORTE}\n\n"
                "Mensaje:\n"
                f"{mensaje_usuario}\n"
            )

            destino = getattr(settings, "SUPPORT_INBOX", settings.DEFAULT_FROM_EMAIL)

            email = EmailMessage(
                subject=ASUNTO_SOPORTE,
                body=cuerpo,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[destino],
                reply_to=[email_usuario],  # para poder responderle directo al usuario
            )

            try:
                email.send(fail_silently=False)
                messages.success(request, "¡Gracias! Tu informe fue enviado correctamente.")
                return redirect("soporte:form")  # redirige para limpiar el POST
            except Exception as e:
                messages.error(request, f"Ocurrió un error al enviar el correo: {e}")
    else:
        form = SoporteForm()

    return render(request, "soporte/soporte.html", {"miSoporte": form})

