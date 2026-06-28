from django import forms

from menus.models import MenuItem


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
            "tenant": "Chọn tenant",
            "group": "Chọn nhóm menu",
            "parent": "Chọn nhóm cha",
            "code": "Mã menu con",
            "label": "Tên nhóm menu con",
            "url_name": "Tên URL",
            "url_path": "Đường dẫn URL",
            "icon": "Icon đại diện (Định dạng svg)",
            "badge_text": "Nhãn tạo (Số)",
            "badge_color": "Màu nhãn tạo",
            "permission_code": "Mã quyền",
            "sort_order": "Thứ tự sắp xếp",
            "open_in_new_tab": "Mở trên tab mới",
            "is_active": "Trạng thái hoạt động",
            "is_hidden": "Trạng thái ẩn",
        }

        labels = {
            "tenant": "Tenant",
            "group": "Nhóm menu",
            "parent": "Nhóm cha",
            "code": "Mã menu con",
            "label": "Tên nhóm menu con",
            "url_name": "Tên URL",
            "url_path": "Đường dẫn URL",
            "icon": "Icon đại diện (Định dạng svg)",
            "badge_text": "Nhãn tạo (Số)",
            "badge_color": "Màu nhãn tạo",
            "permission_code": "Mã quyền",
            "sort_order": "Thứ tự sắp xếp",
            "open_in_new_tab": "Mở trên tab mới",
            "is_active": "Trạng thái hoạt động",
            "is_hidden": "Trạng thái ẩn",
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


class MenuItemBaseForm(TailwindFormMixin, forms.ModelForm):
    """
    Production MenuItem generation form. Handles explicit calendar enforcement
    and handles file uploading logic gracefully.
    """

    class Meta:
        model = MenuItem
        fields = [
            "tenant",
            "group",
            "parent",
            "code",
            "label",
            "url_name",
            "url_path",
            "icon",
            "badge_text",
            "badge_color",
            "permission_code",
            "sort_order",
            "open_in_new_tab",
            "is_active",
            "is_hidden",
        ]
        widgets = {
            # Let template and mixin control specific responsive design attributes
            "is_active": forms.RadioSelect(
                choices=[(True, "Kích hoạt"), (False, "Ngừng kích hoạt")]
            ),
            "is_hidden": forms.RadioSelect(
                choices=[(True, "Hiện"), (False, "Ẩn")]
            ),
        }

    def __init__(self, *args, **kwargs):
        # 1. Call the parent class's init function to initialize the fields and apply Tailwind CSS first.
        super().__init__(*args, **kwargs)
