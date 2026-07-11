import pytest
from decimal import Decimal
from tenants.models.tenants import Tenant
from accounts.models.user_accounts import UserAccount
from branches.models import Branch, BranchAuditLog
from branches.application.dtos import BranchCreateDto, BranchUpdateDto
from branches.providers.branch_provider import BranchProvider


@pytest.mark.django_db
class TestBranchUseCasesAndSignals:

    @pytest.fixture(autouse=True)
    def setup_tenant(self):
        # Create a tenant for test
        self.tenant = Tenant.objects.create(
            code="BRTEST",
            name="Branch Test Tenant",
            plan="STANDARD",
            is_active=True,
        )
        self.user = UserAccount.objects.create_user(
            tenant=self.tenant,
            username="test_actor",
            email="actor@example.com",
            password="securepassword123",
        )

    def test_create_branch_usecase_and_signal(self):
        BranchAuditLog.objects.all().delete()
        Branch.objects.all().delete()

        dto = BranchCreateDto(
            tenant_id=self.tenant.id,
            code="HN_OFFICE",
            name="Hanoi Office",
            address="123 Kim Ma",
            phone="02412345678",
            email="hanoi@domain.com",
            manager_id=None,
            latitude=Decimal("21.0285"),
            longitude=Decimal("105.8542"),
            timezone="Asia/Ho_Chi_Minh",
            is_active=True,
            metadata={"key": "val"},
        )

        use_case = BranchProvider.create_branch()
        entity = use_case.execute(dto, actor_id=self.user.id, actor_username=self.user.username)

        assert entity.id is not None
        assert entity.code == "HN_OFFICE"
        assert entity.name == "Hanoi Office"

        logs = BranchAuditLog.objects.filter(branch_id=entity.id).order_by("created_at")
        assert logs.count() >= 1

        usecase_log = logs.filter(actor_id=self.user.id).first()
        assert usecase_log is not None
        assert usecase_log.action == "CREATE"
        assert usecase_log.actor_username == self.user.username
        assert usecase_log.new_values["code"] == "HN_OFFICE"

    def test_update_branch_usecase_and_signal(self):
        branch_model = Branch.objects.create(
            tenant=self.tenant,
            code="SG_DEPOT",
            name="Saigon Depot",
            address="456 Nguyen Hue",
            phone="02812345678",
            email="saigon@domain.com",
            latitude=Decimal("10.7765"),
            longitude=Decimal("106.7009"),
            timezone="Asia/Ho_Chi_Minh",
            is_active=True,
            metadata={},
        )

        dto = BranchUpdateDto(
            id=branch_model.id,
            code="SG_DEPOT",
            name="Saigon Depot Updated",
            address="456 Nguyen Hue (New)",
            phone="02812345678",
            email="saigon@domain.com",
            manager_id=None,
            latitude=Decimal("10.7765"),
            longitude=Decimal("106.7009"),
            timezone="Asia/Ho_Chi_Minh",
            is_active=True,
            metadata={"capacity": 1000},
        )

        use_case = BranchProvider.update_branch()
        entity = use_case.execute(dto, actor_id=self.user.id, actor_username=self.user.username)

        assert entity.name == "Saigon Depot Updated"
        assert entity.address == "456 Nguyen Hue (New)"

        logs = BranchAuditLog.objects.filter(branch_id=branch_model.id, actor_id=self.user.id)
        assert logs.count() >= 1
        update_log = logs.first()
        assert update_log.action == "UPDATE"
        assert update_log.old_values["name"] == "Saigon Depot"
        assert update_log.new_values["name"] == "Saigon Depot Updated"

    def test_delete_branch_usecase_and_signal(self):
        branch_model = Branch.objects.create(
            tenant=self.tenant,
            code="DN_HUB",
            name="Danang Hub",
            address="789 Tran Phu",
            phone="02361234567",
            email="danang@domain.com",
            latitude=Decimal("16.0544"),
            longitude=Decimal("108.2022"),
            timezone="Asia/Ho_Chi_Minh",
            is_active=True,
            metadata={},
        )

        # 1. Test Soft Delete
        use_case = BranchProvider.soft_delete_branch()
        use_case.execute(branch_model.id, actor_id=self.user.id, actor_username=self.user.username)

        # In safedelete, objects are hidden from default manager but exist in all_objects
        assert not Branch.objects.filter(id=branch_model.id).exists()
        assert Branch.all_objects.filter(id=branch_model.id).exists()

        logs = BranchAuditLog.objects.filter(actor_id=self.user.id)
        assert logs.count() >= 1
        delete_log = logs.first()
        assert delete_log.action == "DELETE"
        assert delete_log.old_values["code"] == "DN_HUB"

        # 2. Test Hard Delete
        hard_use_case = BranchProvider.hard_delete_branch()
        hard_use_case.execute(branch_model.id, actor_id=self.user.id, actor_username=self.user.username)

        # Verify completely gone from DB
        assert not Branch.all_objects.filter(id=branch_model.id).exists()

        # Since Branch is hard deleted and branch FK on BranchAuditLog has on_delete=CASCADE,
        # the audit log entries related to this branch will also be deleted.
        assert BranchAuditLog.objects.filter(branch_id=branch_model.id).count() == 0
