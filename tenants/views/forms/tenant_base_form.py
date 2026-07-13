from django import forms

from tenants.models.tenants import Tenant


class TailwindFormMixin:
    """
    Mixin to automatically apply Tailwind CSS classes to all fields.
    Keeps layout styles unified and clean across the application.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tailwind_classes = (
            "w-full border-[1.5px] border-gray-200 rounded-md bg-white transition-all "
            "hover:border-blue-400 focus:border-blue-500 focus:ring-0 "
            "dark:bg-slate-800 dark:border-slate-700 dark:text-gray-200 px-4 py-3 text-sm"
        )

        placeholders = {
            "code": "VD: DINHANH, VEXPRESS",
            "name": "Nhập tên công ty hoặc nhà xe",
            "domain": "https://example.com",
            "exchange_rate": "1.0000",
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
            "created_at": "Ngày tạo",
            "updated_at": "Ngày cập nhật",
            "deleted_at": "Ngày xóa",
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

            elif isinstance(widget, (forms.DateInput, forms.DateTimeInput)):
                picker_type = (
                    "datetime-picker" if isinstance(widget, forms.DateTimeInput) else ""
                )
                widget.attrs.update(
                    {
                        "class": f"{tailwind_classes} flatpickr-input {picker_type}".strip(),
                        "placeholder": current_placeholder,
                        "autocomplete": "off",
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


class TenantBaseForm(TailwindFormMixin, forms.ModelForm):
    """
    Production Tenant generation form. Handles explicit calendar enforcement
    and handles file uploading logic gracefully.
    """

    logo_url = forms.ImageField(
        required=False,
        help_text="Chọn tệp ảnh logo từ máy tính của bạn.",
        label="Tải ảnh logo lên",
    )
    created_at = forms.DateTimeField(
        required=False, disabled=True, widget=forms.DateTimeInput()
    )
    updated_at = forms.DateTimeField(
        required=False, disabled=True, widget=forms.DateTimeInput()
    )
    deleted_at = forms.DateTimeField(
        required=False, disabled=True, widget=forms.DateTimeInput()
    )

    class Meta:
        model = Tenant
        fields = [
            "code",
            "name",
            "domain",
            "primary_color",
            "plan",
            "currency",
            "exchange_rate",
            "default_language",
            "timezone",
            "is_active",
            "subscription_started_at",
            "subscription_expires_at",
            "max_users",
            "max_branches",
            "max_vehicles",
            "settings",
        ]
        widgets = {
            "primary_color": forms.TextInput(attrs={"type": "color"}),
            "is_active": forms.RadioSelect(
                choices=[(True, "Kích hoạt"), (False, "Ngừng kích hoạt")]
            ),
            "subscription_started_at": forms.DateTimeInput(),
            "subscription_expires_at": forms.DateTimeInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            for field in ["subscription_started_at", "subscription_expires_at"]:
                if self.instance.__dict__.get(field):
                    self.fields[field].initial = self.instance.__dict__[field].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

            for readonly_field in ["created_at", "updated_at", "deleted_at"]:
                val = getattr(self.instance, readonly_field, None)
                if val:
                    self.fields[readonly_field].initial = val.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

        if "exchange_rate" in self.fields:
            self.fields["exchange_rate"].required = False

        if "logo_url" in self.fields:
            self.fields["logo_url"].required = False
