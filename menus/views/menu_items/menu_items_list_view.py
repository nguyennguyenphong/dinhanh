from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View


class MenuItemListView(LoginRequiredMixin, View):
    """
    Handle the rendering of the menu list page.
    Follows MVT pattern:
    1. Extract filters from request.GET
    2. Execute Service/Provider logic
    3. Render the template with the provided context
    """

    def get(self, request):
        return render(request, "pages/menu_items/list.html")
