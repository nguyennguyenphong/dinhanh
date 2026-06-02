from django.apps import AppConfig


class SharedConfig(AppConfig):
    name = "shared"

    def ready(self):
        try:
            import shared.components.ui.button
            import shared.components.ui.input
            import shared.components.ui.checkbox
            import shared.components.ui.select
            import shared.components.ui.page_header
            import shared.components.ui.datepicker
            import shared.components.ui.fileuploader
        except ImportError:
            pass