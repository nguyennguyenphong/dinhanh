import pytest

from accounts.models.roles import Role
from menus.application.dtos.menu_item_roles import (
    MenuItemRoleCreateDto,
)
from menus.application.usecases.menu_item_roles import (
    CreateMenuItemRoleUseCase,
)
from menus.models import MenuItem
from menus.repositories.implement.menu_item_repository_impl import (
    MenuItemRepositoryImpl,
)
from menus.repositories.implement.menu_item_role_repository_impl import (
    MenuItemRoleRepositoryImpl,
)
from tenants.models.tenants import Tenant


@pytest.mark.django_db
class TestMenuItemRoleRepository:
    def test_create_and_get_by_id(self):
        tenant = Tenant.objects.create(code="ROLE1", name="Role Tenant 1")
        menu_item = MenuItem.objects.create(
            tenant=tenant,
            code="item1",
            label="Item 1",
            url_path="/item1",
        )
        role = Role.objects.create(
            tenant=tenant,
            name="Role 1",
            slug="role-1",
        )
        repo = MenuItemRoleRepositoryImpl()
        assignment = repo.create(menu_item=menu_item, role=role)
        assert assignment.id is not None
        assert assignment.menu_item_id == menu_item.id
        assert assignment.role_id == role.id
        retrieved = repo.get_by_id(assignment.id)
        assert retrieved is not None
        assert retrieved.menu_item_id == menu_item.id


@pytest.mark.django_db
class TestMenuItemRoleUseCases:
    def test_create_menu_item_role_success(self):
        tenant = Tenant.objects.create(code="ROLE2", name="Role Tenant 2")
        menu_item = MenuItem.objects.create(
            tenant=tenant,
            code="item2",
            label="Item 2",
            url_path="/item2",
        )
        role = Role.objects.create(
            tenant=tenant,
            name="Role 2",
            slug="role-2",
        )

        menu_item_role_repo = MenuItemRoleRepositoryImpl()
        menu_item_repo = MenuItemRepositoryImpl()
        usecase = CreateMenuItemRoleUseCase(menu_item_role_repo, menu_item_repo)

        dto = MenuItemRoleCreateDto(
            menu_item_id=menu_item.id,
            role_id=role.id,
        )

        res = usecase.execute(dto)
        assert res.menu_item_id == menu_item.id
        assert res.role_id == role.id

    def test_create_menu_item_role_tenant_mismatch_fails(self):
        tenant1 = Tenant.objects.create(code="R3A", name="Tenant A")
        tenant2 = Tenant.objects.create(code="R3B", name="Tenant B")

        menu_item = MenuItem.objects.create(
            tenant=tenant1,
            code="item3",
            label="Item 3",
            url_path="/item3",
        )
        role = Role.objects.create(
            tenant=tenant2,
            name="Role 3",
            slug="role-3",
        )

        menu_item_role_repo = MenuItemRoleRepositoryImpl()
        menu_item_repo = MenuItemRepositoryImpl()
        usecase = CreateMenuItemRoleUseCase(menu_item_role_repo, menu_item_repo)

        dto = MenuItemRoleCreateDto(
            menu_item_id=menu_item.id,
            role_id=role.id,
        )

        with pytest.raises(ValueError, match="same tenant"):
            usecase.execute(dto)
