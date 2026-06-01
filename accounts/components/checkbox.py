from django_components import Component, register


@register("checkbox")
class Checkbox(Component):
    template_file = "components/ui/checkbox.html"

    def get_context_data(
        self,
        name="",
        id=None,
        label="",
        checked=False,
        required=False,
        disabled=False,
        help_text=None,
        error=None,
        input_class="",
        wrapper_class="",
        **attrs,
    ):
        return {
            "name": name,
            "id": id or name,
            "label": label,
            "checked": checked,
            "required": required,
            "disabled": disabled,
            "help_text": help_text,
            "error": error,
            "input_class": input_class,
            "wrapper_class": wrapper_class,
            "attrs": attrs,
        }
