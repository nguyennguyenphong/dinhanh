from django import forms

from menus.models import MenuGroup


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

        placeholders = {
            "code": "Ví dụ: TRANGCHU, DANGNHAP",
            "label": "Tên nhóm menu",
        }

        labels = {
            "tenant": "Chọn mã tenant",
            "code": "Mã nhóm menu",
            "label": "Tên nhóm menu",
            "icon": "Icon đại diện (Định dạng svg)",
            "sort_order": "Thứ tự sắp xếp",
            "is_active": "Trạng thái hoạt động",
        }

        for field_name, field in self.fields.items():
            if field_name in labels:
                field.label = labels[field_name]

            widget = field.widget
            current_placeholder = placeholders.get(field_name, "")

            # Check if it is a color input first to prevent text class overriding
            if isinstance(
                widget,
                (forms.TextInput, forms.NumberInput),
            ):
                widget.attrs.update(
                    {
                        "class": tailwind_classes,
                        "placeholder": current_placeholder,
                        "autocomplete": "off",
                    }
                )

            elif isinstance(widget, forms.Select):
                widget.attrs.update({"class": tailwind_classes.replace("px-4", "px-3")})

            elif isinstance(widget, forms.Textarea):
                widget.attrs.update(
                    {
                        "class": (
                            f"{tailwind_classes} font-mono "
                            "text-xs leading-6 resize-y min-h-[200px]"
                        ),
                    }
                )


class MenuGroupBaseForm(TailwindFormMixin, forms.ModelForm):
    """
    Production MenuGroup generation form. Handles explicit calendar enforcement
    and handles file uploading logic gracefully.
    """

    class Meta:
        model = MenuGroup
        fields = [
            "tenant",
            "code",
            "label",
            "icon",
            "sort_order",
            "is_active",
        ]
        widgets = {
            # Let template and mixin control specific responsive design attributes
            "is_active": forms.RadioSelect(
                choices=[(True, "Kích hoạt"), (False, "Ngừng kích hoạt")]
            ),
        }

    def __init__(self, *args, **kwargs):
        # 1. Call the parent class's init function to initialize the fields and apply Tailwind CSS first.
        super().__init__(*args, **kwargs)
