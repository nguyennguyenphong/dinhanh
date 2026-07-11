from django.apps import AppConfig


class BranchesConfig(AppConfig):
    name = "branches"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import branches.signals.branch_signals  # noqa
