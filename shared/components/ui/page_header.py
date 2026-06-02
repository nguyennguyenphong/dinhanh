from django_components import component

@component.register("page_header")
class PageHeader(component.Component):
    template_name = "components/ui/page_header.html"

    def get_context_data(self, title="", description=None, **kwargs):
        return {
            "title": title,
            "description": description,
        }