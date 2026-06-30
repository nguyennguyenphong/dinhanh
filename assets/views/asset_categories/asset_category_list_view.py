from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View


class AssetCategoryListView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "pages/asset_categories/list.html")
