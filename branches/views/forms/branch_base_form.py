from django import forms

from branches.models import Branch


class TailwindFormMixin:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        tailwind_classes = (
            "w-full border-[1.5px] border-gray-200 rounded-md bg-white transition-all "
            "hover:border-blue-400 focus:border-blue-500 focus:ring-0 "
            "dark:bg-slate-800 dark:border-slate-700 dark:text-gray-200 px-4 py-3 text-sm"
        )

        labels = {
            "tenant": "Tổ chức/Doanh nghiệp sở hữu",
            "code": "Mã chi nhánh",
            "name": "Tên chi nhánh",
            "address": "Địa chỉ",
            "phone": "Số điện thoại",
            "email": "Email liên hệ",
            "manager": "Người quản lý",
            "latitude": "Vĩ độ (Latitude)",
            "longitude": "Kinh độ (Longitude)",
            "timezone": "Múi giờ",
            "is_active": "Trạng thái",
            "metadata": "Metadata cấu hình (JSON)",
        }

        placeholders = {
            "code": "Ví dụ: HCM_DISTRICT_1",
            "name": "Ví dụ: Chi nhánh Quận 1 - HCMC",
            "address": "Nhập địa chỉ cơ sở...",
            "phone": "Ví dụ: 02812345678",
            "email": "Ví dụ: support.hcm@domain.com",
            "latitude": "Ví dụ: 10.7765",
            "longitude": "Ví dụ: 106.7009",
            "metadata": 'Ví dụ: {"region": "South", "capacity": 500}',
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
                    forms.DateInput,
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

            elif isinstance(widget, forms.Textarea):
                widget.attrs.update(
                    {
                        "class": tailwind_classes,
                        "placeholder": current_placeholder,
                    }
                )

            elif isinstance(widget, forms.RadioSelect):
                widget.attrs.update(
                    {
                        "class": "w-4 h-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    }
                )


class BranchBaseForm(TailwindFormMixin, forms.ModelForm):
    class Meta:
        model = Branch
        fields = [
            "tenant",
            "code",
            "name",
            "address",
            "phone",
            "email",
            "manager",
            "latitude",
            "longitude",
            "timezone",
            "is_active",
            "metadata",
        ]
        widgets = {
            "tenant": forms.Select(),
            "code": forms.TextInput(),
            "name": forms.TextInput(),
            "address": forms.Textarea(attrs={"rows": 4}),
            "phone": forms.TextInput(),
            "email": forms.EmailInput(),
            "manager": forms.Select(),
            "latitude": forms.NumberInput(),
            "longitude": forms.NumberInput(),
            "timezone": forms.Select(),
            "is_active": forms.RadioSelect(
                choices=[(True, "Đang hoạt động"), (False, "Ngừng hoạt động")]
            ),
            "metadata": forms.Textarea(attrs={"rows": 5}),
        }
