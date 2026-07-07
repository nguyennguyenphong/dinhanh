import pytest

from menus.application.dtos.menu_items import (
    MenuItemCreateDto,
    MenuItemUpdateDto,
)
from menus.application.usecases.menu_items import (
    CreateMenuItemUseCase,
    UpdateMenuItemUseCase,
)
from menus.exceptions import (
    MenuItemAlreadyExistsError,
)
from menus.repositories.implement.menu_item_repository_impl import (
    MenuItemRepositoryImpl,
)
from menus.serializers.menu_items import (
    MenuItemCreateSerializer,
)
from tenants.models.tenants import Tenant


@pytest.mark.django_db
class TestMenuItemRepository:
    def test_create_and_get_by_id(self):
        tenant = Tenant.objects.create(code="TEST", name="Test Tenant")
        repo = MenuItemRepositoryImpl()

        # Test creation
        item = repo.create(
            tenant_id=tenant.id,
            code="test_item",
            label="Test Item",
            url_path="/test",
        )

        assert item.id is not None
        assert item.code == "test_item"
        assert item.label == "Test Item"

        # Test retrieval
        retrieved = repo.get_by_id(item.id)
        assert retrieved is not None
        assert retrieved.code == "test_item"

    def test_exists_with_code(self):
        tenant = Tenant.objects.create(code="TEST2", name="Test Tenant 2")
        repo = MenuItemRepositoryImpl()

        assert not repo.exists_with_code(tenant.id, "exists_code")

        repo.create(
            tenant_id=tenant.id,
            code="exists_code",
            label="Exists Item",
            url_path="/exists",
        )

        assert repo.exists_with_code(tenant.id, "exists_code")


@pytest.mark.django_db
class TestMenuItemUseCases:
    def test_create_menu_item_success(self):
        tenant = Tenant.objects.create(code="T3", name="Tenant 3")
        repo = MenuItemRepositoryImpl()
        usecase = CreateMenuItemUseCase(repo)

        dto = MenuItemCreateDto(
            tenant=tenant.id,
            code="item_success",
            label="Success Item",
            url_path="/success",
        )

        res = usecase.execute(dto)
        assert res.code == "item_success"
        assert res.label == "Success Item"

    def test_create_menu_item_duplicate_code_fails(self):
        tenant = Tenant.objects.create(code="T4", name="Tenant 4")
        repo = MenuItemRepositoryImpl()
        usecase = CreateMenuItemUseCase(repo)

        repo.create(
            tenant_id=tenant.id,
            code="duplicate",
            label="Duplicate Item",
            url_path="/dup",
        )

        dto = MenuItemCreateDto(
            tenant=tenant.id,
            code="duplicate",
            label="Another Duplicate",
            url_path="/another",
        )

        with pytest.raises(MenuItemAlreadyExistsError):
            usecase.execute(dto)

    def test_circular_parent_fails(self):
        tenant = Tenant.objects.create(code="T5", name="Tenant 5")
        repo = MenuItemRepositoryImpl()
        usecase = UpdateMenuItemUseCase(repo)

        item = repo.create(
            tenant_id=tenant.id,
            code="circular",
            label="Circular",
            url_path="/circ",
        )

        dto = MenuItemUpdateDto(
            id=item.id,
            uuid=item.uuid,
            code="circular",
            label="Circular",
            parent_id=item.id,
        )

        with pytest.raises(ValueError, match="cannot be its own parent"):
            usecase.execute(dto)


@pytest.mark.django_db
class TestMenuItemSerializers:
    def test_create_serializer_validation(self):
        tenant = Tenant.objects.create(code="T6", name="Tenant 6")
        data = {
            "tenant": tenant.id,
            "code": "SERIALIZER",
            "label": "Serializer Item",
            "url_path": "/serializer",
        }

        serializer = MenuItemCreateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_create_serializer_missing_url_fails(self):
        tenant = Tenant.objects.create(code="T7", name="Tenant 7")
        data = {
            "tenant": tenant.id,
            "code": "NOURL",
            "label": "No URL Item",
        }

        serializer = MenuItemCreateSerializer(data=data)
        assert not serializer.is_valid()
