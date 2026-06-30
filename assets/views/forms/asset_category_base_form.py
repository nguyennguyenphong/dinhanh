from django import forms

from assets.models import AssetCategory


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
            "name": "Tên danh mục tài sản",
        }

        placeholders = {
            "tenant": "Chọn mã doanh nghiệp sở hữu...",
            "name": "Ví dụ: Thiết bị văn phòng, Máy móc nặng, Xe tải vận tải...",
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
                    }
                )

            elif isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                widget.attrs.update(
                    {
                        "class": "h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    }
                )


class AssetCategoryBaseForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = AssetCategory
        fields = [
            "tenant",
            "name",
        ]
        widgets = {
            "tenant": forms.Select(),
            "name": forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["tenant"].label = "Tenant"
        self.fields["name"].label = "Tên danh mục"

        placeholders = {
            "name": "Nhập tên danh mục tài sản",
        }

        for field_name, placeholder in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs["placeholder"] = placeholder