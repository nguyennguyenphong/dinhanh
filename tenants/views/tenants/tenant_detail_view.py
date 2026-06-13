import uuid

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.views import View

from tenants.exceptions.exception import TenantDomainError
from tenants.providers import TenantProvider
from tenants.views.helpers.view_helpers import RequestContext


class TenantDetailView(LoginRequiredMixin, View):
    """
    Handle viewing and deactivating a tenant in MVT style.
    """

    def get(self, request, pk: uuid.UUID):
        try:
            # Call provider to get tenant data
            try:
                tenant = TenantProvider.get_tenant().by_uuid(pk)
            except Exception:
                raise Http404("Tenant không tồn tại")
        except TenantDomainError as e:
            return render(request, "portals/404.html", {"error": str(e)})

        return render(request, "pages/detail.html", {"tenant": tenant})
