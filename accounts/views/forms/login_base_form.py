from django import forms


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
            "email": "example@gmail.com",
            "password": "••••••••",
        }

        labels = {
            "email": "Email",
            "password": "Mật khẩu",
        }

        for field_name, field in self.fields.items():
            if field_name in labels:
                field.label = labels[field_name]

            widget = field.widget
            current_placeholder = placeholders.get(field_name, "")

            if isinstance(widget, (forms.EmailInput, forms.PasswordInput, forms.TextInput)):
                widget.attrs.update(
                    {
                        "class": tailwind_classes,
                        "placeholder": current_placeholder,
                        "autocomplete": "off",
                    }
                )


class LoginBaseForm(TailwindFormMixin, forms.Form):
    """
    Production standard login form capturing raw customer interface strings.
    Utilizes TailwindFormMixin to cleanly apply visual properties.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(),
        error_messages={'required': 'Please enter your email address.'}
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(),
        error_messages={'required': 'Please enter your password.'}
    )