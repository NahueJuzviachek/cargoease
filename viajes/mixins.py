from django.conf import settings

class ORSContextMixin:
    """
    Mixin liviano para inyectar la API key de ORS (u otros valores) al contexto.
    No hereda de Model ni usa metaclases.
    """
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["ORS_API_KEY"] = getattr(settings, "ORS_API_KEY", "")
        # agrega acá lo que necesites, p.ej. perfiles ORS, flags, etc.
        # ctx["ORS_PROFILE"] = "driving-hgv"
        return ctx