from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST


def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password"),
        )
        if user:
            login(request, user)
            messages.success(request, f"Bienvenido, {user.username} 👋")
            return redirect("home")
        messages.error(request, "Usuario o contraseña incorrectos.")
    return render(request, "registration/login.html")

@require_POST
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Sesión cerrada correctamente.")
    # Si no estaba autenticado, igual lo llevamos al login
    return redirect("login")