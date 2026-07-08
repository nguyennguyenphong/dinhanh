from django import forms

from accounts.models import Permission


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
            "codename": "Mã quyền (Codename)",
            "name": "Tên quyền",
            "module": "Tên Module",
            "action": "Hành động (Action)",
            "description": "Mô tả chi tiết",
            "parent": "Quyền cha",
            "is_active": "Trạng thái hoạt động",
        }

        placeholders = {
            "codename": "Ví dụ: tickets.add_ticket",
            "name": "Ví dụ: Có quyền thêm vé xe",
            "module": "Ví dụ: tickets",
            "description": "Nhập mô tả chi tiết quyền hạn...",
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


class PermissionBaseForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Permission
        fields = [
            "tenant",
            "codename",
            "name",
            "module",
            "action",
            "description",
            "parent",
            "is_active",
        ]
        widgets = {
            "tenant": forms.Select(),
            "codename": forms.TextInput(),
            "name": forms.TextInput(),
            "module": forms.TextInput(),
            "action": forms.Select(),
            "description": forms.Textarea(attrs={"rows": 2}),
            "parent": forms.Select(),
            "is_active": forms.Select(
                choices=[(True, "Đang hoạt động"), (False, "Ngừng hoạt động")]
            ),
        }
