# aceite/apps.py
from django.apps import AppConfig

class AceiteConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "aceite"

    def ready(self):
        # registra señales
        from . import signals  # noqa: F401
