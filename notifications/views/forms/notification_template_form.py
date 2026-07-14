from django import forms

from notifications.models.notification_templates import NotificationTemplate


class TailwindFormMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tailwind_classes = (
            "w-full border-[1.5px] border-gray-200 rounded-md bg-white transition-all "
            "hover:border-blue-400 focus:border-blue-500 focus:ring-0 "
            "dark:bg-slate-800 dark:border-slate-700 dark:text-gray-200 px-4 py-3 text-sm"
        )

        placeholders = {
            "code": "VD: OTP_VERIFICATION, TRIP_CANCELLED",
            "name": "Nhập tên mẫu thông báo",
            "body": "Nhập nội dung mẫu với các biến động (VD: {otp_code})",
        }

        labels = {
            "tenant": "Đơn vị Tenant",
            "code": "Mã mẫu thông báo",
            "name": "Tên mẫu thông báo",
            "channel": "Kênh gửi",
            "subject": "Tiêu đề (nếu có)",
            "body": "Nội dung mẫu",
            "variables": "Biến động cho phép",
            "is_active": "Trạng thái hoạt động",
        }

        for field_name, field in self.fields.items():
            if field_name in labels:
                field.label = labels[field_name]

            widget = field.widget
            current_placeholder = placeholders.get(field_name, "")

            if isinstance(
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

            elif isinstance(widget, forms.Textarea):
                widget.attrs.update(
                    {
                        "class": (
                            f"{tailwind_classes} font-mono "
                            "text-xs leading-6 resize-y min-h-[150px]"
                        )
                    }
                )


class NotificationTemplateForm(TailwindFormMixin, forms.ModelForm):

    class Meta:
        model = NotificationTemplate
        fields = [
            "tenant",
            "code",
            "name",
            "channel",
            "subject",
            "body",
            "variables",
            "is_active",
        ]
        widgets = {
            "is_active": forms.RadioSelect(
                choices=[(True, "Kích hoạt"), (False, "Ngừng kích hoạt")]
            ),
        }
