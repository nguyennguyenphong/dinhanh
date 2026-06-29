from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from menus.models import MenuItemRole


class TailwindFormMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tailwind_classes = (
            "w-full border-[1.5px] border-gray-200 rounded-md bg-white transition-all "
            "hover:border-blue-400 focus:border-blue-500 focus:ring-0 "
            "dark:bg-slate-800 dark:border-slate-700 dark:text-gray-200 px-4 py-3 text-sm"
        )

        placeholders = {
            "menu_item": "Chọn mục menu áp dụng...",
            "role": "Chọn vai trò được phép truy cập...",
        }

        labels = {
            "menu_item": "Mục Menu (Menu Item)",
            "role": "Vai trò (Role)",
        }

        for field_name, field in self.fields.items():
            if field_name in labels:
                field.label = labels[field_name]

            widget = field.widget

            if isinstance(widget, forms.Select):
                widget.attrs.update({"class": tailwind_classes.replace("px-4", "px-3")})


class MenuItemRoleBaseForm(TailwindFormMixin, forms.ModelForm):

    class Meta:
        model = MenuItemRole
        fields = [
            "menu_item",
            "role",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        menu_item = cleaned_data.get("menu_item")
        role = cleaned_data.get("role")

        if menu_item and role:
            if menu_item.tenant_id != role.tenant_id:
                raise ValidationError(
                    _("Mục menu và vai trò được chọn phải thuộc về cùng một doanh nghiệp (Tenant).")
                )
                
        return cleaned_data