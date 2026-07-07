from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from menus.services.menu_item_role_service import MenuItemRoleService
from menus.views.forms.menu_item_role_form import MenuItemRoleBaseForm


class MenuItemRoleCreateView(LoginRequiredMixin, View):
    """
    Handle MenuItemRole assignment creation.
    """

    def get(self, request):
        form = MenuItemRoleBaseForm()
        return render(request, "pages/menu_item_roles/create.html", {"form": form})

    def post(self, request):
        form = MenuItemRoleBaseForm(request.POST)

        if form.is_valid():
            success = MenuItemRoleService.create_menu_item_role(request, form)

            if success:
                messages.success(request, "Role assigned to menu item successfully.")
                return redirect("menu_item_role_list")

        return render(request, "pages/menu_item_roles/create.html", {"form": form})
