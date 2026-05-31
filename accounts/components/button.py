from django_components import Component, register

@register("button")
class Button(Component):
    template_file = "components/ui/button.html"

    def get_context_data(
        self,
        text="Button",
        type="button",
        variant="primary",
        size="md",
        icon=None,
        icon_right=None,
        disabled=False,
        loading=False,
        full_width=False,
        button_class="",
        **attrs,
    ):
        return {
            "text": text,
            "type": type,
            "variant": variant,
            "size": size,
            "icon": icon,
            "icon_right": icon_right,
            "disabled": disabled,
            "loading": loading,
            "full_width": full_width,
            "button_class": button_class,
            "attrs": attrs,
        }