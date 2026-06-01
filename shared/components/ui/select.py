import json
from django_components import Component, register


@register("select")
class Select(Component):
    template_file = "components/ui/select.html"

    def get_context_data(
        self,
        label=None,
        name="",
        id=None,
        value="",
        placeholder="Chọn một tùy chọn...",
        options=None,
        required=False,
        disabled=False,
        size="md",
        color="blue",
        error=None,
        help_text=None,
        wrapper_class="",
        **attrs,
    ):
        if isinstance(options, str):
            try:
                options = json.loads(options)
            except json.JSONDecodeError:
                options = []
        else:
            options = options or []

        element_id = id or f"select_{name}"

        size_configs = {
            "sm": {"btn": "py-2 px-3 text-xs rounded-lg", "icon": "w-3.5 h-3.5"},
            "md": {"btn": "py-3 px-4 text-sm rounded-xl", "icon": "w-4 h-4"},
            "lg": {"btn": "py-4 px-5 text-base rounded-2xl", "icon": "w-5 h-5"},
        }
        size_style = size_configs.get(size, size_configs["md"])

        color_configs = {
            "blue": {
                "focus": "border-blue-500 focus:ring-2 focus:ring-blue-500/20 hover:border-blue-400",
                "bg_active": "bg-blue-500 text-white dark:bg-blue-600",
            },
            "emerald": {
                "focus": "border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 hover:border-emerald-400",
                "bg_active": "bg-emerald-500 text-white dark:bg-emerald-600",
            },
            "amber": {
                "focus": "border-amber-500 focus:ring-2 focus:ring-amber-500/20 hover:border-amber-400",
                "bg_active": "bg-amber-500 text-white dark:bg-amber-600",
            },
        }
        color_style = color_configs.get(color, color_configs["blue"])

        initial_label = placeholder
        search_value = str(value) if value is not None else ""
        
        for opt in options:
            if str(opt.get("value", "")) == search_value:
                initial_label = opt.get("label")
                break

        return {
            "label": label,
            "name": name,
            "id": element_id,
            "value": value,
            "placeholder": placeholder,
            "options_data": options,
            "initial_label": initial_label,
            "required": required,
            "disabled": disabled,
            "error": error,
            "help_text": help_text,
            "size_style": size_style,
            "color_style": color_style,
            "wrapper_class": wrapper_class,
            "attrs": attrs,
        }