from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from menus.models import MenuItemRole
from menus.views.forms.menu_item_role_form import MenuItemRoleBaseForm


class MenuItemRoleUpdateView(LoginRequiredMixin, View):
    """
    Handle MenuItemRole assignment update.
    """

    def get(self, request, pk: uuid.UUID):
        menu_item_role = get_object_or_404(MenuItemRole, uuid=pk)
        form = MenuItemRoleBaseForm(instance=menu_item_role)
        return render(
            request,
            "pages/menu_item_roles/update.html",
            {"form": form, "menu_item_role": menu_item_role},
        )

    def post(self, request, pk: uuid.UUID):
        return self.patch(request, pk)

    def patch(self, request, pk: uuid.UUID):
        menu_item_role = get_object_or_404(MenuItemRole, uuid=pk)
        form = MenuItemRoleBaseForm(request.POST, instance=menu_item_role)

        if form.is_valid():
            if not form.has_changed():
                messages.info(request, "Dữ liệu không thay đổi.")
                return render(
                    request,
                    "pages/menu_item_roles/update.html",
                    {"form": form, "menu_item_role": menu_item_role},
                )
            form.save()
            messages.success(request, "Role assignment updated successfully.")
            return redirect("menu_item_role_update", pk=menu_item_role.uuid)

        return render(
            request,
            "pages/menu_item_roles/update.html",
            {"form": form, "menu_item_role": menu_item_role},
        )
