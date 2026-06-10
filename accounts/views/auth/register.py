from django.shortcuts import render


def register(request):
    static_roles = [
        {"value": "dispatcher", "label": "Nhân viên điều vận"},
        {"value": "cashier", "label": "Nhân viên bán vé"},
        {"value": "manager", "label": "Quản lý"},
        {"value": "driver", "label": "Tài xế / Lái xe"},
    ]

    selected_role_value = "cashier"

    context = {
        "my_options": static_roles,
        "default_value": selected_role_value,
        "label_name": "Vai trò nhân sự",
    }

    return render(request, "pages/register.html", context)
