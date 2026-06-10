from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from tenants.exceptions.exception import TenantDomainError
from tenants.providers import TenantProvider
from tenants.views.helpers.view_helpers import RequestContext


class TenantDetailView(LoginRequiredMixin, View):
    """
    Handle viewing and deactivating a tenant in MVT style.
    """

    def get(self, request, pk: int):
        try:
            # Call provider to get tenant data
            tenant = TenantProvider.get_tenant().by_id(pk)
        except TenantDomainError as e:
            return render(request, "pages/404.html", {"error": str(e)})

        return render(request, "pages/detail.html", {"tenant": tenant})

    def post(self, request, pk: int):
        """
        Handle deactivation via POST (standard for forms in MVT).
        """
        ctx = RequestContext.from_request(request)
        try:
            TenantProvider.deactivate_tenant().execute(
                pk,
                actor_id=ctx.actor_id,
                actor_username=ctx.actor_username,
                ip_address=ctx.ip_address,
                user_agent=ctx.user_agent,
            )
        except TenantDomainError:
            # Handle error (maybe show a message on the detail page)
            pass

        return redirect("tenant_list")  # Redirect back to list after action
