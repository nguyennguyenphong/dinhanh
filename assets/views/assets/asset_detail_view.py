from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View


class AssetDetailView(LoginRequiredMixin, View):
    """
    Handle viewing and deactivating a menu group in MVT style.
    """

    def get(self, request):

        return render(request, "pages/assets/detail.html")
