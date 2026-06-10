from django import forms
from django.core.files.storage import default_storage


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
            "code": "VD: DINHANH, VEXPRESS",
            "name": "Nhập tên công ty hoặc nhà xe",
            "domain": "https://example.com",
            "exchange_rate": "1.0000",
            "search_tenant": "Tìm kiếm tên tenant, code",
        }

        labels = {
            "code": "Mã tenant",
            "name": "Tên tenant",
            "domain": "Tên miền",
            "logo_url": "Tải ảnh logo lên",
            "primary_color": "Màu chủ đạo",
            "plan": "Gói dịch vụ",
            "currency": "Tiền tệ",
            "exchange_rate": "Tỷ giá",
            "default_language": "Ngôn ngữ mặc định",
            "timezone": "Múi giờ",
            "is_active": "Trạng thái hoạt động",
            "max_users": "Số người dùng tối đa",
            "max_branches": "Số chi nhánh tối đa",
            "max_vehicles": "Số phương tiện tối đa",
            "settings": "Cài đặt khác",
            "subscription_started_at": "Ngày bắt đầu",
            "subscription_expires_at": "Ngày kết thúc",
            "search_tenant": "Tìm kiếm",
            "sort_by": "Sắp xếp theo",
            "status": "Trạng thái",
            "created_at": "Ngày tạo",
        }

        for field_name, field in self.fields.items():
            if field_name in labels:
                field.label = labels[field_name]

            widget = field.widget
            current_placeholder = placeholders.get(field_name, "")

            if (
                isinstance(widget, forms.TextInput)
                and widget.attrs.get("type") == "color"
            ):
                widget.attrs.update(
                    {
                        "class": "h-10 w-12 p-0.5 block bg-transparent border border-gray-200 rounded-md cursor-pointer dark:border-slate-700"
                    }
                )

            elif isinstance(
                widget,
                (forms.TextInput, forms.EmailInput, forms.URLInput, forms.NumberInput),
            ):
                widget.attrs.update(
                    {
                        "class": tailwind_classes,
                        "placeholder": current_placeholder,
                        "autocomplete": "off",
                    }
                )

            elif isinstance(widget, (forms.DateInput, forms.DateTimeInput)):
                widget.attrs.update(
                    {
                        "class": tailwind_classes,
                    }
                )

            elif isinstance(widget, forms.Select):
                widget.attrs.update({"class": tailwind_classes.replace("px-4", "px-3")})

            elif isinstance(widget, forms.FileInput):
                widget.attrs.update(
                    {
                        "class": (
                            "block w-full text-sm text-gray-500 "
                            "border border-gray-200 rounded-md "
                            "dark:border-slate-700 dark:text-gray-300 "
                            "file:mr-4 file:py-3 file:px-4 "
                            "file:rounded-md file:border-0 "
                            "file:text-sm file:font-medium "
                            "file:bg-blue-50 file:text-blue-700 "
                            "hover:file:bg-blue-100 pl-4"
                        )
                    }
                )

            elif isinstance(widget, forms.Textarea):
                widget.attrs.update(
                    {
                        "class": (
                            f"{tailwind_classes} font-mono "
                            "text-xs leading-6 resize-y min-h-[200px]"
                        )
                    }
                )

            if isinstance(widget, forms.CheckboxSelectMultiple):
                widget.attrs.update({"class": checkbox_classes})


class TenantFilterForm(TailwindFormMixin, forms.Form):
    """
    This form is used to handle search data and advanced filters for the Tenant list.
    It inherits TailwindFormMixin to automatically map the CSS interface synchronously.
    """

    SORT_CHOICES = [
        ("", "Sắp xếp theo"),
        ("az", "Tên: A → Z"),
        ("za", "Tên: Z → A"),
        ("latest", "Mới nhất"),
        ("oldest", "Cũ nhất"),
    ]

    STATUS_CHOICES = [
        ("all", "Tất cả trạng thái"),
        ("True", "Hoạt động"),
        ("False", "Khóa"),
    ]

    PLAN_CHOICES = [
        ("all", "Tất cả gói"),
        ("free", "Free"),
        ("pro", "Pro"),
    ]

    COLUMN_CHOICES = [
        ("code", "Code"),
        ("name", "Tên Tenant"),
    ]

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

    created_at = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )

    columns = forms.MultipleChoiceField(
        choices=COLUMN_CHOICES,
        required=False,
        initial=["code", "name"],
        widget=forms.CheckboxSelectMultiple(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["sort_by"].widget.choices[0] = ("", "Sắp xếp theo")
