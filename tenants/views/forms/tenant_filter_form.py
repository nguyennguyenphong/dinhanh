from django import forms

from tenants.constants import PLAN_CHOICES, SORT_CHOICES, STATUS_CHOICES


class TailwindFormMixin:
    """
    Mixin to automatically apply Tailwind CSS classes to all fields.
    Keeps layout styles unified and clean across the application.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Standard input class configuration
        tailwind_classes = (
            "w-full border-[1.5px] border-gray-200 rounded-md bg-white transition-all "
            "hover:border-blue-400 focus:border-blue-500 focus:ring-0 "
            "dark:bg-slate-800 dark:border-slate-700 dark:text-gray-200 px-4 py-3 text-sm"
        )

        checkbox_classes = "w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 cursor-pointer"

        placeholders = {
            "search_tenant": "Tìm kiếm tên tenant, code",
            "plan": "Tìm kiếm gói dịch vụ",
            "status": "Tìm kiếm trạng thái",
        }

        for field_name, field in self.fields.items():

            widget = field.widget
            current_placeholder = placeholders.get(field_name, "")

            if isinstance(
                widget,
                (forms.TextInput),
            ):
                widget.attrs.update(
                    {
                        "class": tailwind_classes,
                        "placeholder": current_placeholder,
                        "autocomplete": "off",
                    }
                )

            elif isinstance(widget, forms.Select):
                widget.attrs.update({"class": tailwind_classes})

            elif isinstance(widget, forms.CheckboxSelectMultiple):
                widget.attrs.update({"class": checkbox_classes})


class TenantFilterForm(TailwindFormMixin, forms.Form):
    """
    This form is used to handle search data and advanced filters for the Tenant list.
    It inherits TailwindFormMixin to automatically map the CSS interface synchronously.
    """

    search_tenant = forms.CharField(required=False, widget=forms.TextInput())

    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES, required=False, widget=forms.Select()
    )

    status = forms.ChoiceField(
        choices=STATUS_CHOICES, required=False, initial="all", widget=forms.Select()
    )

    plan = forms.ChoiceField(
        choices=PLAN_CHOICES, required=False, initial="all", widget=forms.Select()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["sort_by"].widget.choices[0] = ("", "Sắp xếp theo")
