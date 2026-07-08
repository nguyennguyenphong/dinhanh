from django import forms

from accounts.models import PermissionGroup


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
            "code": "Mã nhóm quyền",
            "name": "Tên nhóm quyền",
            "description": "Mô tả chi tiết",
            "permissions": "Danh sách các quyền",
            "is_active": "Trạng thái hoạt động",
        }

        placeholders = {
            "code": "Ví dụ: tickets_full_access",
            "name": "Ví dụ: Toàn quyền quản lý vé",
            "description": "Nhập mô tả các quyền hạn của nhóm...",
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

            elif isinstance(widget, forms.SelectMultiple):
                # Multiple select styling
                widget.attrs.update(
                    {
                        "class": (
                            "w-full border-[1.5px] border-gray-200 rounded-md bg-white "
                            "dark:bg-slate-800 dark:border-slate-700 dark:text-gray-200 "
                            "px-3 py-2 text-sm min-h-[150px]"
                        )
                    }
                )

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


class PermissionGroupBaseForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = PermissionGroup
        fields = [
            "tenant",
            "code",
            "name",
            "description",
            "permissions",
            "is_active",
        ]
        widgets = {
            "tenant": forms.Select(),
            "code": forms.TextInput(),
            "name": forms.TextInput(),
            "description": forms.Textarea(attrs={"rows": 2}),
            "permissions": forms.SelectMultiple(),
            "is_active": forms.Select(
                choices=[(True, "Đang hoạt động"), (False, "Ngừng hoạt động")]
            ),
        }
