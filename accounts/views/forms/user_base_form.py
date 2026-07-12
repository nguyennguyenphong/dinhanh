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

            if isinstance(
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
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If we are updating an existing user, password should not be required
        if self.instance and self.instance.pk:
            self.fields["password"].required = False
            self.fields["password"].help_text = "Để trống nếu không muốn đổi mật khẩu."
