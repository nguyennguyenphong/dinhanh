from django import forms

from accounts.views.forms.register_base_form import TailwindFormMixin


class ForgotPasswordForm(TailwindFormMixin, forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "example@gmail.com"}),
    )


class ConfirmPasswordResetForm(TailwindFormMixin, forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"placeholder": "example@gmail.com", "readonly": "readonly"}
        ),
    )
    code = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "123456"}),
        label="Mã OTP",
    )
    new_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••"}),
        label="Mật khẩu mới",
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"placeholder": "••••••••"}),
        label="Xác nhận mật khẩu",
    )

    def clean(self):
        cleaned_data = super().clean()
        new_pass = cleaned_data.get("new_password")
        confirm_pass = cleaned_data.get("confirm_password")
        if new_pass != confirm_pass:
            raise forms.ValidationError("Mật khẩu xác nhận không khớp.")
        return cleaned_data


class VerifyEmailForm(TailwindFormMixin, forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"placeholder": "example@gmail.com", "readonly": "readonly"}
        ),
    )
    code = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "123456"}),
        label="Mã OTP",
    )
