from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.models import Role
from accounts.views.forms.role_base_form import RoleBaseForm


class RoleUpdateView(LoginRequiredMixin, View):

    def get(self, request, pk: int):
        role = get_object_or_404(Role, id=pk)
        form = RoleBaseForm(instance=role)
        return render(
            request,
            "pages/role_create.html",  # Re-use create template for edit
            {"form": form, "object": role, "is_update": True},
        )

    def post(self, request, pk: int):
        role = get_object_or_404(Role, id=pk)
        form = RoleBaseForm(request.POST, instance=role)

        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Cập nhật vai trò thành công.")
                return redirect("role_list")
            except Exception as exc:
                form.add_error(None, str(exc))
                messages.error(request, f"Lỗi cập nhật vai trò: {str(exc)}")

        return render(
            request,
            "pages/role_create.html",
            {"form": form, "object": role, "is_update": True},
        )
