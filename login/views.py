from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST

def login_view(request):
    """
    Muestra el formulario de login y procesa la autenticación.
    Si las credenciales son correctas, inicia sesión y redirige a 'home'.
    Si no, muestra mensaje de error.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Bienvenido, {user.username}")
            return redirect("home")
        messages.error(request, "Usuario o contraseña incorrectos.")
    return render(request, "registration/login.html")


@require_POST
def logout_view(request):
    """
    Cierra la sesión del usuario autenticado y redirige al login.
    """
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Sesión cerrada correctamente.")
    return redirect("login")
