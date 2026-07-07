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
        import tenants.signals.tenant_signals  # noqa
