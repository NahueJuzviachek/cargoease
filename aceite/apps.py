from django.apps import AppConfig

class AceiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aceite"

    def ready(self):
        # Importa señales
        from . import signals  # noqa
