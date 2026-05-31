from django_components import Component, register


@register("input")
class Input(Component):
    template_file = "components/ui/input.html"

    def get_context_data(
        self,
        label=None,
        name="",
        type="text",
        id=None,
        value="",
        placeholder="",
        icon=None,
        required=False,
        disabled=False,
        readonly=False,
        size="md",
        help_text=None,
        error=None,
        input_class="",
        wrapper_class="",
        **attrs,
    ):
        return {
            "label": label,
            "name": name,
            "type": type,
            "id": id or name,
            "value": value,
            "placeholder": placeholder,
            "icon": icon,
            "required": required,
            "disabled": disabled,
            "readonly": readonly,
            "size": size,
            "help_text": help_text,
            "error": error,
            "input_class": input_class,
            "wrapper_class": wrapper_class,
            "attrs": attrs,
        }