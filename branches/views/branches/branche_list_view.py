from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View


class BranchListView(LoginRequiredMixin, View):

    def get(self, request):
        return render(request, "pages/branches/list.html")
