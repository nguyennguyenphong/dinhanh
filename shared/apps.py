from django.apps import AppConfig


class SharedConfig(AppConfig):
    name = "shared"

    def ready(self):
        try:
            import shared.components.ui.button
            import shared.components.ui.input
            import shared.components.ui.checkbox
            import shared.components.ui.select
        except ImportError:
            pass