"""
AppConfig for the Tenant bounded context.
Registers signals and admin once all models are ready.
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TenantAppConfig(AppConfig):
    name = "tenants"
    label = "tenants"
    verbose_name = _("Tenants")
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        # Register signal handlers
        import tenants.signals  # noqa: F401

        # Register admin classes after all models are loaded
        try:
            from tenants.admin import register_admin
            register_admin()
        except Exception:
            # Admin registration failure must never crash the app startup
            import logging
            logging.getLogger(__name__).exception(
                "Failed to register tenant admin classes."
            )