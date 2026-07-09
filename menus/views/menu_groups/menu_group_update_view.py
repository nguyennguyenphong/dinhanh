from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from menus.models import MenuGroup
from menus.services import MenuGroupService
from menus.views.forms import MenuGroupBaseForm


class MenuGroupUpdateView(LoginRequiredMixin, View):
    """
    GET    /menu_groups/update/<pk>/  - menu group edit page
    POST   /menu_groups/update/<pk>/  - routes to patch method
    PATCH  /menu_groups/update/<pk>/  - performs the partial update
    """

    def get(self, request, pk: uuid.UUID):
        menu_group = get_object_or_404(MenuGroup, uuid=pk)
        return render(
            request,
            "pages/menu_groups/update.html",
            {"form": MenuGroupBaseForm(instance=menu_group), "object": menu_group},
        )

    def post(self, request, pk: uuid.UUID):
        return self.patch(request, pk)

    def patch(self, request, pk: uuid.UUID):
        menu_group = get_object_or_404(MenuGroup, uuid=pk)
        form = MenuGroupBaseForm(request.POST, instance=menu_group)

        if form.is_valid():
            if MenuGroupService.update_menu_group(request, pk, form):
                messages.success(request, "Cập nhật nhóm menu thành công.")
                return redirect("menu_group_update", pk=menu_group.uuid)

        return render(
            request,
            "pages/menu_groups/update.html",
            {"form": form, "object": menu_group},
        )
