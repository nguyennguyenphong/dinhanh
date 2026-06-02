import json
from django_components import Component, register


@register("datepicker")
class DatePicker(Component):
    template_file = "components/ui/datepicker.html"

    def get_context_data(
        self,
        label=None,
        name="",
        value="",
        placeholder="Select date...",
        required=False,
        disabled=False,
        readonly=False,
        size="md",
        help_text=None,
        error=None,
        wrapper_class="",
        input_class="",
        mode="single",             
        min_date="",               
        max_date="",               
        disable_dates=None,        
        disable_weekends=False,    
        enable_time=False,         
        **attrs,
    ):
        if disable_dates is None:
            disable_dates = []

        flatpickr_attrs = {
            "data-cms-datepicker": "",
            "data-mode": mode,
            "data-min-date": min_date,
            "data-max-date": max_date,
            "data-enable-time": str(enable_time).lower(),
            "data-disable-weekends": str(disable_weekends).lower(),
            "data-disable-dates": json.dumps(disable_dates),
        }

        attrs.update(flatpickr_attrs)

        return {
            "label": label,
            "name": name,
            "id": attrs.get("id") or name,
            "value": value,
            "placeholder": placeholder,
            "required": required,
            "disabled": disabled,
            "readonly": readonly,
            "size": size,
            "help_text": help_text,
            "error": error,
            "wrapper_class": wrapper_class,
            "input_class": input_class,
            "attrs": attrs,  
        }