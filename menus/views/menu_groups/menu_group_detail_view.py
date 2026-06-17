import uuid

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from menus.services import MenuGroupService


class MenuGroupDetailView(LoginRequiredMixin, View):
    """
    Handle viewing and deactivating a menu group in MVT style.
    """

    def get(self, request, pk: uuid.UUID):
        menu_group = MenuGroupService.get_by_uuid(pk)

        return render(
            request, "pages/menu_groups/detail.html", {"menu_group": menu_group}
        )
