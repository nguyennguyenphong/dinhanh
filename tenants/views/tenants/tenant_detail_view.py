from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View
import uuid

from tenants.services import TenantService


class TenantDetailView(LoginRequiredMixin, View):
    """
    Handle viewing and deactivating a tenant in MVT style.
    """

    def get(self, request, pk: uuid.UUID):
        tenant = TenantService.get_by_uuid(pk)

        return render(request, "pages/detail.html", {"tenant": tenant})
