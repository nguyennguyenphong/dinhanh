from django import forms

from notifications.models.notifications import Notification


class TailwindFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tailwind_classes = (
            "w-full border-[1.5px] border-gray-200 rounded-md bg-white transition-all "
            "hover:border-blue-400 focus:border-blue-500 focus:ring-0 "
            "dark:bg-slate-800 dark:border-slate-700 dark:text-gray-200 px-4 py-3 text-sm"
        )

        placeholders = {
            "tenant_id": "1",
            "recipient_id": "VD: 8901",
            "recipient_phone": "VD: +84909123456",
            "recipient_email": "example@domain.com",
            "channel": "VD: SMS, EMAIL, PUSH, ZALO",
            "subject": "Nhập tiêu đề hoặc chủ đề thông báo",
            "body": "Nhập nội dung thông báo...",
            "retry_count": "0",
            "error_msg": "Nội dung lỗi kỹ thuật (nếu có)",
            "ref_type": "VD: booking, trip, consignment",
            "ref_id": "VD: 5502",
        }

        labels = {
            "tenant_id": "ID Tenant",
            "template": "Mẫu thông báo",
            "recipient_type": "Loại người nhận",
            "recipient_id": "ID người nhận",
            "recipient_phone": "Số điện thoại",
            "recipient_email": "Email người nhận",
            "channel": "Kênh gửi",
            "subject": "Tiêu đề",
            "body": "Nội dung thông báo",
            "status": "Trạng thái",
            "retry_count": "Số lần thử lại",
            "error_msg": "Thông báo lỗi",
            "ref_type": "Loại tham chiếu",
            "ref_id": "ID tham chiếu",
            "sent_at": "Thời gian gửi",
            "created_at": "Ngày tạo",
            "updated_at": "Ngày cập nhật",
            "deleted_at": "Ngày xóa",
        }

        for field_name, field in self.fields.items():
            if field_name in labels:
                field.label = labels[field_name]

            widget = field.widget
            current_placeholder = placeholders.get(field_name, "")

            if isinstance(widget, (forms.DateInput, forms.DateTimeInput)):
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
                        "class": tailwind_classes,
                        "placeholder": current_placeholder,
                    }
                )


class NotificationBaseForm(TailwindFormMixin, forms.ModelForm):
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
        model = Notification
        fields = [
            "tenant_id",
            "template",
            "recipient_type",
            "recipient_id",
            "recipient_phone",
            "recipient_email",
            "channel",
            "subject",
            "body",
            "status",
            "retry_count",
            "error_msg",
            "ref_type",
            "ref_id",
            "sent_at",
        ]
        widgets = {
            "sent_at": forms.DateTimeInput(),
            "body": forms.Textarea(attrs={"rows": 7}),
            "error_msg": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            for field in ["sent_at"]:
                if self.instance.__dict__.get(field):
                    self.fields[field].initial = self.instance.__dict__[field].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

            for readonly_field in ["created_at", "updated_at"]:
                val = getattr(self.instance, readonly_field, None)
                if val:
                    self.fields[readonly_field].initial = val.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
