from django.contrib import admin
from .models import Cliente

# Register your models here.
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "correo", "pais", "provincia", "localidad", "is_active")
    list_filter = ("is_active", "pais")
    search_fields = ("nombre", "correo")