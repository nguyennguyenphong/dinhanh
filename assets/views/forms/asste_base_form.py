from django import forms
from assets.models import Asset

class TailwindFormMixin:
    """
    Mixin to automatically apply Tailwind CSS classes to all fields.
    Keeeps layout styles unified and clean across the application.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tailwind_classes = (
            "w-full border-[1.5px] border-gray-200 rounded-md bg-white transition-all "
            "hover:border-blue-400 focus:border-blue-500 focus:ring-0 "
            "dark:bg-slate-800 dark:border-slate-700 dark:text-gray-200 px-4 py-3 text-sm"
        )

        for field_name, field in self.fields.items():
            widget = field.widget

            if isinstance(widget, (forms.TextInput, forms.NumberInput, forms.EmailInput, forms.PasswordInput, forms.DateInput)):
                widget.attrs.update({
                    "class": tailwind_classes,
                })

            elif isinstance(widget, forms.Select):
                widget.attrs.update({
                    "class": tailwind_classes.replace("px-4", "px-3")
                })

            elif isinstance(widget, forms.Textarea):
                widget.attrs.update({
                    "class": (
                        f"{tailwind_classes} font-mono "
                        "text-xs leading-6 resize-y min-h-[120px]"
                    ),
                })
            
            elif isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                widget.attrs.update({
                    "class": "h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                })

class AssetBaseForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            "tenant",
            "category",
            "branch",
            "assigned_to",
            "code",
            "name",
            "serial_number",
            "purchase_date",
            "purchase_price",
            "depreciation_rate",
            "current_value",
            "warranty_expiry",
            "status",
            "notes",
        ]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
            "warranty_expiry": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
            "status": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["tenant"].label = "Tenant"
        self.fields["category"].label = "Danh mục tài sản"
        self.fields["branch"].label = "Chi nhánh"
        self.fields["assigned_to"].label = "Nhân viên quản lý"
        self.fields["code"].label = "Mã tài sản"
        self.fields["name"].label = "Tên tài sản"
        self.fields["serial_number"].label = "Số Serial"
        self.fields["purchase_date"].label = "Ngày mua"
        self.fields["purchase_price"].label = "Giá mua"
        self.fields["depreciation_rate"].label = "Tỷ lệ khấu hao (%)"
        self.fields["current_value"].label = "Giá trị hiện tại"
        self.fields["warranty_expiry"].label = "Ngày hết hạn bảo hành"
        self.fields["status"].label = "Trạng thái"
        self.fields["notes"].label = "Ghi chú"

        # Cập nhật thêm placeholder cho các trường cần thiết
        placeholders = {
            "code": "Ví dụ: ASSET-001",
            "name": "Nhập tên tài sản",
            "purchase_price": "0.00",
            "depreciation_rate": "15.00",
        }
        
        for field_name, placeholder in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs["placeholder"] = placeholder