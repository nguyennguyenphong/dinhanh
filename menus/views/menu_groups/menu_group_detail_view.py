import uuid

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views import View

from menus.models import MenuGroup


class MenuGroupDetailView(LoginRequiredMixin, View):
    """
    Handle viewing and deactivating a menu group in MVT style.
    """

    def get(self, request, pk: uuid.UUID):
        menu_group = get_object_or_404(MenuGroup.all_objects, uuid=pk)

        from tenants.models import Tenant
        tenant = Tenant.objects.filter(pk=menu_group.tenant_id).first()
        tenant_name = tenant.name if tenant else "-"

        return render(
            request,
            "pages/menu_groups/detail.html",
            {"menu_group": menu_group, "tenant_name": tenant_name},
        )
