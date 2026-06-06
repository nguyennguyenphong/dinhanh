# tenants/application/usecases/tenants/list_tenants_use_case.py
from typing import List

from tenants.domain.entities.tenants.tenant_entity import TenantEntity
from tenants.domain.interfaces.tenants.tenant_repository_interface import ITenantRepository


class ListTenantsUseCase:
    def __init__(self, tenant_repo: ITenantRepository):
        self.tenant_repo = tenant_repo

    def execute(self, search_code: str = None) -> List[TenantEntity]:
        """Business logic: Fetch active and optionally filter by code."""
        tenants = self.tenant_repo.get_active_tenants()
        
        if search_code:
            tenants = [t for t in tenants if search_code.lower() in t.code.lower()]
            
        return tenants