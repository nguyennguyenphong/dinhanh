from django import forms
from tenants.models.tenants import Tenant

class TailwindFormMixin:
    """
    Mixin to automatically apply Tailwind CSS classes to all fields.
    This keeps the code clean and maintains consistency across the platform.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Standard Tailwind classes for input fields
        tailwind_classes = (
            "w-full border-[1.5px] border-gray-200 rounded-md bg-white transition-all "
            "hover:border-blue-400 focus:border-blue-500 focus:ring-0 "
            "dark:bg-slate-800 dark:border-slate-700 dark:text-gray-200 px-4 py-3 text-sm"
        )

        placeholders = {
            'code': 'VD: DINHANH, VEXPRESS',
            'name': 'Nhập tên công ty hoặc nhà xe',
            'domain': 'https://example.com',
            'logo_url': 'https://example.com/logo.png',
            'primary_color': '#000000',
            'plan': 'STANDARD',
            'currency': 'VND',
            'exchange_rate': '1.0000',
            'default_language': 'vi',
            'timezone': 'Asia/Ho_Chi_Minh',
            'is_active': 'true',
            'settings': 'Cài đặt',
            'subscription_started_at': 'Ngày bắt đầu',
            'subscription_end_at': 'Ngày kết thúc',
        }

        labels = {
            'code': 'Mã tenant',
            'name': 'Tên tenant',
            'domain': 'Tên miền',
            'logo_url': 'Logo',
            'primary_color': 'Màu chủ đạo',
            'plan': 'Gói dịch vụ',
            'currency': 'Tiền tệ',
            'exchange_rate': 'Tỷ giá',
            'default_language': 'Ngôn ngữ mặc định',
            'timezone': 'Múi giờ',
            'is_active': 'Trạng thái',
            'settings': 'Cài đặt',
            'subscription_started_at': 'Ngày bắt đầu',
            'subscription_end_at': 'Ngày kết thúc',
        }
        
        for field_name, field in self.fields.items():
            # Add placeholder if defined
            if field_name in placeholders:
                field.widget.attrs.update({'placeholder': placeholders[field_name]})

            widget = field.widget

            # Text input
            if isinstance(widget, (
                forms.TextInput,
                forms.EmailInput,
                forms.URLInput,
                forms.NumberInput,
                forms.PasswordInput,
                forms.Textarea,
            )):
                widget.attrs.update({
                    'class': tailwind_classes,
                    'placeholder': placeholders.get(field_name, '')
                })

            # Date
            elif isinstance(widget, forms.DateInput):
                widget.attrs.update({
                    'class': tailwind_classes,
                    'type': 'date'
                })

            # Datetime
            elif isinstance(widget, forms.DateTimeInput):
                widget.attrs.update({
                    'class': tailwind_classes,
                    'type': 'datetime-local'
                })

            # File/Image
            elif isinstance(widget, forms.FileInput):
                widget.attrs.update({
                    'class': 'block w-full text-sm'
                })

            # Select
            elif isinstance(widget, forms.Select):
                widget.attrs.update({
                    'class': tailwind_classes.replace('px-4', 'px-3')
                })

            # Checkbox
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.update({
                    'class': 'h-5 w-5 rounded border-gray-300'
                })

            # Apply labels
            if field_name in labels:
                field.label = labels[field_name]

class TenantCreateForm(TailwindFormMixin, forms.ModelForm):
    """
    Form for creating a new Tenant.
    Includes comprehensive validation and UI configuration.
    """
    class Meta:
        model = Tenant
        fields = [
            'code', 'name', 'domain', 'logo_url', 'primary_color', 
            'plan', 'currency', 'default_language', 'timezone', 'is_active'
        ]
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color', 'class': 'h-12 w-full'}),
            'timezone': forms.Select(attrs={'class': 'w-full'}), # Ensure proper Select styling
        }

    def clean_code(self):
        """Normalize code to uppercase and ensure uniqueness."""
        code = self.cleaned_data.get('code', '').strip().upper()
        if Tenant.objects.filter(code=code).exists():
            raise forms.ValidationError("A tenant with this code already exists.")
        return code

    def clean_domain(self):
        """Sanitize domain input."""
        domain = self.cleaned_data.get('domain')
        return domain.lower().strip() if domain else None

    def clean_name(self):
        """Ensure name is cleaned of leading/trailing whitespaces."""
        return self.cleaned_data.get('name', '').strip()

    def save(self, commit=True):
        """
        Optional: Override save to perform additional logic like 
        initializing default settings JSON or initial quota.
        """
        instance = super().save(commit=False)
        if not instance.settings:
            instance.settings = {} # Ensure JSONField is initialized
        if commit:
            instance.save()
        return instance