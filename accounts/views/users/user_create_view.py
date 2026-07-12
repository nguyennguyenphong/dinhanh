from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views import View

from accounts.services.user_service import UserService
from accounts.views.forms.user_base_form import UserBaseForm


class UserCreateView(LoginRequiredMixin, View):

    def get(self, request):
        form = UserBaseForm()
        return render(request, "pages/users/create.html", {"form": form})

    def post(self, request):
        form = UserBaseForm(request.POST)

        if form.is_valid():
            success = UserService.create_user(request, form)
            if success:
                return redirect("user_list")

        return render(request, "pages/users/create.html", {"form": form})
