from django import forms

from accounts.models import Role


class TailwindFormMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tailwind_classes = (
            "w-full border-[1.5px] border-gray-200 rounded-md bg-white transition-all "
            "hover:border-blue-400 focus:border-blue-500 focus:ring-0 "
            "dark:bg-slate-800 dark:border-slate-700 dark:text-gray-200 px-4 py-3 text-sm"
        )

        labels = {
            "tenant": "Doanh nghiệp",
            "name": "Tên vai trò",
            "slug": "Mã vai trò (Slug)",
            "description": "Mô tả vai trò",
            "is_active": "Trạng thái",
        }

        placeholders = {
            "name": "Ví dụ: Quản lý cửa hàng",
            "slug": "Ví dụ: shop-manager",
            "description": "Nhập mô tả quyền hạn và trách nhiệm của vai trò...",
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
                            "text-xs leading-6 resize-y min-h-[100px]"
                        ),
                        "placeholder": current_placeholder,
                    }
                )


class RoleBaseForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Role
        fields = [
            "tenant",
            "name",
            "slug",
            "description",
            "is_active",
        ]
        widgets = {
            "tenant": forms.Select(),
            "name": forms.TextInput(),
            "slug": forms.TextInput(),
            "description": forms.Textarea(attrs={"rows": 3}),
            "is_active": forms.Select(
                choices=[(True, "Đang hoạt động"), (False, "Ngừng hoạt động")]
            ),
        }
