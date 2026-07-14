from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from accounts.models import UserAccount
from accounts.services.user_service import UserService
from accounts.views.forms.user_base_form import UserBaseForm


class UserUpdateView(LoginRequiredMixin, View):

    def get(self, request, pk: int):
        user = get_object_or_404(UserAccount, id=pk)
        form = UserBaseForm(instance=user)
        return render(
            request,
            "pages/users/update.html",
            {"form": form, "object": user, "is_update": True},
        )

    def post(self, request, pk: int):
        return self.patch(request, pk)

    def patch(self, request, pk: int):
        user = get_object_or_404(UserAccount, id=pk)
        form = UserBaseForm(request.POST, instance=user)

        if form.is_valid():
            success = UserService.update_user(request, pk, form)
            if success:
                return redirect("user_update", pk=user.id)

        return render(
            request,
            "pages/users/update.html",
            {"form": form, "object": user, "is_update": True},
        )
