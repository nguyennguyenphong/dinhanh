"""
DRF API views for Tenant CRUD operations.

Endpoint map (wired in urls/tenant_urls.py):
    PATCH  /tenants/<pk>/  — partial update
"""

from __future__ import annotations

import uuid

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from menus.models import MenuGroup

# from menus.policies import TenantPolicy
from menus.services.menu_group_service import MenuGroupService
from menus.views.forms import MenuGroupBaseForm


class MenuGroupUpdateView(LoginRequiredMixin, View):
    """
    GET    /menu_group/<pk>/  - tenant detail
    PATCH  /menu_group/<pk>/  — partial update
    """

    def get(self, request, pk: uuid.UUID):
        menu_group = get_object_or_404(MenuGroup, uuid=pk)
        return render(
            request,
            "pages/menu_groups/update.html",
            {"form": MenuGroupBaseForm(instance=menu_group), "object": menu_group},
        )

    """
    Django does not support direct patching from HTML forms.
    We map POST to PATCH by calling the patch method.
    """
