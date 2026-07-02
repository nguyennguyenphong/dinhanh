from django import forms
from branches.models import Branch

class TailwindFormMixin:
    
    placeholders = {}
    labels = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tailwind_classes = (
            "w-full border-[1.5px] border-gray-200 rounded-md bg-white transition-all "
            "hover:border-blue-400 focus:border-blue-500 focus:ring-0 "
            "dark:bg-slate-800 dark:border-slate-700 dark:text-gray-200 px-4 py-3 text-sm"
        )

        for field_name, field in self.fields.items():
            if field_name in self.labels:
                field.label = self.labels[field_name]

            widget = field.widget
            placeholder = self.placeholders.get(field_name, "")

            # Color/Text/Number inputs
            if isinstance(widget, (forms.TextInput, forms.NumberInput, forms.EmailInput)):
                widget.attrs.update({
                    "class": tailwind_classes,
                    "placeholder": placeholder,
                    "autocomplete": "off"
                })
            
            # Select inputs
            elif isinstance(widget, forms.Select):
                widget.attrs.update({"class": tailwind_classes.replace("px-4", "px-3")})
            
            # Textarea
            elif isinstance(widget, forms.Textarea):
                widget.attrs.update({
                    "class": f"{tailwind_classes} font-mono text-xs leading-6 resize-y"
                })
            
            # Checkbox / Radio
            elif isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                widget.attrs.update({"class": "w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"})

class BranchBaseForm(TailwindFormMixin, forms.ModelForm):
    """
    Base form for Branch model with integrated Tailwind styling.
    """

    class Meta:
        model = Branch
        fields = [
            "tenant", "code", "name", "address", "phone", 
            "email", "manager", "latitude", "longitude", 
            "timezone", "is_active", "metadata"
        ]
        widgets = {
            "is_active": forms.RadioSelect(
                choices=[(True, "Đang hoạt động"), (False, "Ngừng hoạt động")],
            ),
            "address": forms.Textarea(attrs={"rows": 3}),
            "metadata": forms.Textarea(attrs={"placeholder": '{"key": "value"}'}),
            "timezone": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        self.placeholders.update({
            "code": "Ví dụ: HCM",
            "name": "Nhập tên chi nhánh",
            "address": "Nhập địa chỉ chi nhánh",
            "phone": "Nhập số điện thoại",
            "email": "Nhập email liên hệ",
            "latitude": "Ví dụ: 10.7765",
            "longitude": "Ví dụ: 106.7009",
        })
        
        self.labels.update({
            "code": "Mã chi nhánh",
            "name": "Tên chi nhánh",
            "address": "Địa chỉ",
            "phone": "Số điện thoại",
            "email": "Email liên hệ",
            "manager": "Người quản lý",
            "latitude": "Vĩ độ",
            "longitude": "Kinh độ",
            "timezone": "Múi giờ",
            "is_active": "Trạng thái",
            "metadata": "Cấu hình Metadata (JSON)",
        })
        
        super().__init__(*args, **kwargs)
        
        if 'tenant' in self.fields:
            self.fields['tenant'].widget.attrs.update({'readonly': 'readonly'})