# tenants/domain/interfaces/tenants/tenant_repository_interface.py
from abc import ABC, abstractmethod
from typing import List, Optional
from tenants.domain.entities.tenants.tenant_entity import TenantEntity

class ITenantRepository(ABC):
    @abstractmethod
    def get_active_tenants(self) -> List[TenantEntity]:
        pass

    @abstractmethod
    def get_by_code(self, code: str) -> Optional[TenantEntity]:
        pass