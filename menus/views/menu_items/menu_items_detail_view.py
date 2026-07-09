from __future__ import annotations

import uuid

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views import View

from menus.models import MenuItem


class MenuItemDetailView(LoginRequiredMixin, View):
    """
    Handle viewing menu item details in MVT style.
    """

    def get(self, request, pk: uuid.UUID):
        menu_item = get_object_or_404(MenuItem.all_objects, uuid=pk)

        from tenants.models import Tenant

        tenant = Tenant.objects.filter(pk=menu_item.tenant_id).first()
        tenant_name = tenant.name if tenant else "-"

        return render(
            request,
            "pages/menu_items/detail.html",
            {"menu_item": menu_item, "tenant_name": tenant_name},
        )
