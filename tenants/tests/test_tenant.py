import pytest
from tenants.application.dtos import TenantCreateDTO
from tenants.application.usecases import CreateTenantUseCase
from tenants.exceptions import TenantAlreadyExistsError


class TestCreateTenantUseCase:
    def test_creates_tenant_successfully(self, make_entity, mock_repos):

        tenant_repo, audit_repo = mock_repos()
        tenant_repo.exists_by_code.return_value = False
        saved = make_entity()
        tenant_repo.create.return_value = saved

        uc = CreateTenantUseCase(tenant_repo, audit_repo)
        dto = TenantCreateDTO(code="DEMO", name="Demo Bus")
        result = uc.execute(dto, actor_id=1, actor_username="admin")

        assert result.code == "DEMO"