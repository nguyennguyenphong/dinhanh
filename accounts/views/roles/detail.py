from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.views import View

from accounts.models import Role


class RoleDetailView(LoginRequiredMixin, View):

    def get(self, request, pk: int):
        role = get_object_or_404(Role, id=pk)
        return render(
            request,
            "pages/role_detail.html",
            {"role": role},
        )
