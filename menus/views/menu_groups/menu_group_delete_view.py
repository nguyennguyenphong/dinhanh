from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import Form
from django.shortcuts import redirect
from django.views import View

from menus.services import MenuGroupService


class MenuGroupSoftDeleteView(LoginRequiredMixin, View):
    """
    Handle MenuGroup soft deletion.
    """

    def post(self, request, pk: uuid.UUID):
        form = Form(request.POST)
        success = MenuGroupService.soft_delete_menu_group(request, pk, form)
        if success:
            messages.success(request, "Menu group deleted successfully.")
        return redirect("menu_group_list")


class MenuGroupHardDeleteView(LoginRequiredMixin, View):
    """
    Handle MenuGroup hard deletion.
    """

    def post(self, request, pk: uuid.UUID):
        form = Form(request.POST)
        success = MenuGroupService.hard_delete_menu_group(request, pk, form)
        if success:
            messages.success(request, "Menu group permanently deleted.")
        return redirect("menu_group_list")
