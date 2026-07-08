from django import forms

from assets.models import StorageUnit


class TailwindFormMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tailwind_classes = (
            "w-full border-[1.5px] border-gray-200 rounded-md bg-white transition-all "
            "hover:border-blue-400 focus:border-blue-500 focus:ring-0 "
            "dark:bg-slate-800 dark:border-slate-700 dark:text-gray-200 px-4 py-3 text-sm"
        )

        labels = {
            "tenant": "Tổ chức/Doanh nghiệp sở hữu",
            "branch": "Chi nhánh/Cơ sở lưu trữ",
            "code": "Mã kho bãi",
            "name": "Tên kho bãi",
            "description": "Mô tả chi tiết",
        }

        placeholders = {
            "tenant": "Chọn mã doanh nghiệp sở hữu...",
            "branch": "Chọn chi nhánh...",
            "code": "Ví dụ: KHO_LOGISTICS_Q5",
            "name": "Ví dụ: Kho chính Mộc Bài",
            "description": "Nhập mô tả capacity hoặc ghi chú...",
        }

        for field_name, field in self.fields.items():
            if field_name in labels:
                field.label = labels[field_name]

            widget = field.widget
            current_placeholder = placeholders.get(field_name, "")

            if isinstance(
                widget,
                (
                    forms.TextInput,
                    forms.NumberInput,
                    forms.EmailInput,
                    forms.PasswordInput,
                    forms.DateInput,
                ),
            ):
                widget.attrs.update(
                    {
                        "class": tailwind_classes,
                        "placeholder": current_placeholder,
                    }
                )

            elif isinstance(widget, forms.Select):
                widget.attrs.update({"class": tailwind_classes.replace("px-4", "px-3")})

            elif isinstance(widget, forms.Textarea):
                widget.attrs.update(
                    {
                        "class": (
                            f"{tailwind_classes} font-mono "
                            "text-xs leading-6 resize-y min-h-[120px]"
                        ),
                        "placeholder": current_placeholder,
                    }
                )


class StorageUnitBaseForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = StorageUnit
        fields = [
            "tenant",
            "branch",
            "code",
            "name",
            "description",
        ]
        widgets = {
            "tenant": forms.Select(),
            "branch": forms.Select(),
            "code": forms.TextInput(),
            "name": forms.TextInput(),
            "description": forms.Textarea(),
        }
