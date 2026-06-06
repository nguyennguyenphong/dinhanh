# tenants/interfaces/view_models/tenants/tenant_view_model.py
from typing import List

from tenants.domain.entities.tenants.tenant_entity import TenantEntity


class TenantListItemViewModel:
    """
    Defines exactly what the View needs.
    Formats data for display.
    """
    def __init__(self, tenant: TenantEntity):
        self.id = tenant.id
        # Example of formatting: Ensure display name is uppercase
        self.display_name = f"TENANT: {tenant.code.upper()}"
        # Example of business-logic-based field: Display status string instead of boolean
        self.status_label = "Active" if tenant.is_active else "Inactive"
        # Example of hiding sensitive data
        self.short_uuid = str(tenant.uuid)[:8] + "..."

class TenantListViewModel:
    """
    Holds the collection and page-level metadata.
    """
    def __init__(self, tenants: List[TenantEntity], total_count: int):
        self.items = [TenantListItemViewModel(t) for t in tenants]
        self.total_count = total_count
        self.has_tenants = total_count > 0