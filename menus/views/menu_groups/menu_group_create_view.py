"""
DRF API views for Menu CRUD operations.

Endpoint map (wired in urls/menu_urls.py):
    POST   /menus/                -> MenuListView
"""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from menus.services import MenuGroupService
from menus.views.forms import MenuGroupBaseForm


class MenuGroupCreateView(LoginRequiredMixin, View):
    """
    Handle Menu creation:
    1. GET: Render the creation form.
    2. POST: Validate data, process file upload, execute UseCase, and redirect.
    """

    def get(self, request):
        form = MenuGroupBaseForm()
        return render(request, "pages/menu_groups/create.html", {"form": form})

    def post(self, request):
        form = MenuGroupBaseForm(request.POST)

        if form.is_valid():
            success = MenuGroupService.create_menu_group(request, form)

            if success:
                messages.success(request, "Nhóm menu tạo thành công.")
                return redirect("menu_group_list")

        return render(request, "pages/menu_groups/create.html", {"form": form})
