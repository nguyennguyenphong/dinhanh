import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from django.views import View

from tenants.application.dtos import TenantListQueryDTO
from tenants.exceptions.exception import TenantDomainError
from tenants.providers import TenantProvider
from tenants.views.forms import TenantFilterForm

# class TenantListView(LoginRequiredMixin, View):
#     """
#     Handle the rendering of the tenant list page.
#     Follows MVT pattern:
#     1. Extract filters from request.GET via TenantFilterForm
#     2. Execute Service/Provider logic
#     3. Render the template with the provided context
#     """

#     def get(self, request):
#         form = TenantFilterForm(request.GET or None)

#         search_value = request.GET.get("search_tenant", "")
#         plan_value = request.GET.get("plan")
#         status_value = request.GET.get("status")

#         if form.is_valid():
#             search_value = form.cleaned_data.get("search_tenant")
#             plan_value = form.cleaned_data.get("plan")
#             status_value = form.cleaned_data.get("status")

#         is_active = None
#         if status_value == "True":
#             is_active = True
#         elif status_value == "False":
#             is_active = False

#         if plan_value == "all":
#             plan_value = None

#         query_dto = TenantListQueryDTO(
#             search=search_value,
#             plan=plan_value,
#             is_active=is_active,
#             limit=int(request.GET.get("limit", 10)),
#             offset=int(request.GET.get("offset", 0)),
#         )

#         try:
#             tenants, total = TenantProvider.list_tenants().execute(query_dto)
#         except TenantDomainError as e:
#             return render(request, "pages/list.html", {"error": str(e), "form": form})


#         context = {
#             "tenants": tenants,
#             "total": total,
#             "query": query_dto,
#             "form": form,
#         }
#         return render(request, "pages/tenants/list.html", context)
class TenantListView(LoginRequiredMixin, View):
    def get(self, request):
        form = TenantFilterForm(request.GET or None)

        # Giữ nguyên logic lấy dữ liệu từ Provider của bạn
        # Ở đây set limit lớn hoặc lấy tất cả vì ta cần đẩy hết về frontend
        query_dto = TenantListQueryDTO(
            search=request.GET.get("search_tenant", ""),
            plan=request.GET.get("plan"),
            is_active=None,  # Tùy logic của bạn
            limit=1000,  # Lấy số lượng lớn để đẩy về client
            offset=0,
        )

        try:
            tenants, total = TenantProvider.list_tenants().execute(query_dto)
        except TenantDomainError as e:
            return render(
                request, "pages/tenants/list.html", {"error": str(e), "form": form}
            )

        # 1. Chuyển đổi list object sang dạng List of Lists cho Grid.js
        tenants_data = []
        for idx, tenant in enumerate(tenants, start=1):
            tenants_data.append(
                [
                    idx,
                    str(tenant.uuid),
                    tenant.code,
                    tenant.name,
                    tenant.domain or "",
                    tenant.logo_url or "",
                    tenant.primary_color or "",
                    "Kích hoạt" if tenant.is_active else "Ngừng kích hoạt",
                    tenant.max_users,
                    tenant.max_branches,
                    tenant.max_vehicles,
                    tenant.plan or "",
                    tenant.timezone or "",
                    tenant.default_language or "",
                    tenant.currency or "",
                    tenant.exchange_rate,
                    (
                        tenant.created_at.strftime("%H:%M:%S %Y/%m/%d")
                        if tenant.created_at
                        else ""
                    ),
                    (
                        tenant.updated_at.strftime("%H:%M:%S %Y/%m/%d")
                        if tenant.updated_at
                        else ""
                    ),
                    (
                        tenant.deleted.strftime("%H:%M:%S %Y/%m/%d")
                        if hasattr(tenant, "deleted") and tenant.deleted
                        else "None"
                    ),
                    str(tenant.uuid),  # Thao tác
                ]
            )

        # 2. Convert mảng dữ liệu thành chuỗi JSON an toàn
        tenants_json = json.dumps(tenants_data, cls=DjangoJSONEncoder)

        context = {
            "tenants_json": tenants_json,  # Biến JSON tổng
            "form": form,
        }
        return render(request, "pages/tenants/list.html", context)
