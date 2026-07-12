from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from menus.services.menu_item_service import MenuItemService
from menus.views.forms.menu_item_base_form import MenuItemBaseForm


class MenuItemCreateView(LoginRequiredMixin, View):
    """
    Handle MenuItem creation:
    1. GET: Render the creation form.
    2. POST: Validate data, execute UseCase, and redirect.
    """

    def get(self, request):
        form = MenuItemBaseForm()
        return render(request, "pages/menu_items/create.html", {"form": form})

    def post(self, request):
        form = MenuItemBaseForm(request.POST)

        if form.is_valid():
            success = MenuItemService.create_menu_item(request, form)

            if success:
                messages.success(request, "Tạo menu con thành công.")
                return redirect("menu_items_list")

        return render(request, "pages/menu_items/create.html", {"form": form})
