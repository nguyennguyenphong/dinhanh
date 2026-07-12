from django import forms

from accounts.models import UserAccount


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
            "username": "Tên đăng nhập",
            "email": "Email",
            "password": "Mật khẩu",
            "full_name": "Họ và tên",
            "phone": "Số điện thoại",
            "avatar": "Đường dẫn ảnh đại diện (Avatar URL)",
            "branch": "Chi nhánh",
            "is_active": "Trạng thái hoạt động",
            "must_change_password": "Phải đổi mật khẩu",
            "password_expires_at": "Mật khẩu hết hạn",
            "locked_until": "Khóa tài khoản đến ngày",
        }

        placeholders = {
            "username": "Ví dụ: nguyen.van.a",
            "email": "Ví dụ: ana@domain.com",
            "password": "Nhập mật khẩu bảo mật...",
            "full_name": "Ví dụ: Nguyễn Văn A",
            "phone": "Ví dụ: 0912345678",
            "avatar": "Ví dụ: https://domain.com/avatar.jpg",
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
                (
                    forms.TextInput,
                    forms.NumberInput,
                    forms.EmailInput,
                    forms.PasswordInput,
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


class UserBaseForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = UserAccount
        fields = [
            "tenant",
            "username",
            "email",
            "password",
            "full_name",
            "phone",
            "avatar",
            "branch",
            "is_active",
            "must_change_password",
            "password_expires_at",
            "locked_until",
        ]
        widgets = {
            "tenant": forms.Select(),
            "username": forms.TextInput(),
            "email": forms.EmailInput(),
            "password": forms.PasswordInput(),
            "full_name": forms.TextInput(),
            "phone": forms.TextInput(),
            "avatar": forms.TextInput(),
            "branch": forms.Select(),
            "is_active": forms.RadioSelect(
                choices=[(True, "Đang hoạt động"), (False, "Ngừng hoạt động")]
            ),
            "must_change_password": forms.RadioSelect(
                choices=[(True, "Đổi mật khẩu"), (False, "Không đổi mật khẩu")]
            ),
            "password_expires_at": forms.DateTimeInput(),
            "locked_until": forms.DateTimeInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["password"].required = False
            self.fields["password"].help_text = "Để trống nếu không muốn đổi mật khẩu."
            date_fields = ["must_change_password", "password_expires_at", "locked_until"]
            for field in date_fields:
                value = getattr(self.instance, field, None)
                if value:
                    self.fields[field].initial = value.strftime("%Y-%m-%d %H:%M")

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not password:
            return password

        if len(password) < 8:
            raise forms.ValidationError("Mật khẩu phải chứa ít nhất 8 ký tự.")

        import re
        if not re.search(r"[a-z]", password):
            raise forms.ValidationError("Mật khẩu phải chứa ít nhất một chữ cái in thường.")
        if not re.search(r"[A-Z]", password):
            raise forms.ValidationError("Mật khẩu phải chứa ít nhất một chữ cái in hoa.")
        if not re.search(r"[0-9]", password):
            raise forms.ValidationError("Mật khẩu phải chứa ít nhất một chữ số.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise forms.ValidationError("Mật khẩu phải chứa ít nhất một ký tự đặc biệt.")
        return password

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username:
            import re
            if not re.match(r"^[a-zA-Z0-9_]+$", username):
                raise forms.ValidationError(
                    "Tên đăng nhập chỉ được bao gồm chữ cái, chữ số hoặc ký tự gạch dưới (_), không chứa dấu cách hoặc ký tự khác."
                )
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email:
            from django.core.validators import validate_email
            from django.core.exceptions import ValidationError
            try:
                validate_email(email)
            except ValidationError:
                raise forms.ValidationError("Email không đúng định dạng.")
        return email

    def clean_password_expires_at(self):
        date = self.cleaned_data.get("password_expires_at")
        if date:
            from django.utils import timezone
            if date <= timezone.now():
                raise forms.ValidationError("Thời gian mật khẩu hết hạn phải lớn hơn thời gian hiện tại.")
        return date

    def clean_locked_until(self):
        date = self.cleaned_data.get("locked_until")
        if date:
            from django.utils import timezone
            if date <= timezone.now():
                raise forms.ValidationError("Thời gian khóa tài khoản phải lớn hơn thời gian hiện tại.")
        return date
