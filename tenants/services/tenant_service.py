# ============================================================================
# FILE: apps/tenants/services/tenant_service.py
# ============================================================================
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from rest_framework.exceptions import ValidationError

from tenants.repositories.tenant_repository import TenantRepository
from tenants.models.tenants import Tenant
from tenants.tasks.tenant_tasks import provision_tenant_resources_task


class TenantRegistrationService:
    """
    Core Domain Service orchestrating the business workflow for provisioning a new Tenant.
    """
    def __init__(self):
        self.repository = TenantRepository()

    @transaction.atomic
    def execute(self, validated_data: dict) -> Tenant:
        """
        Executes the explicit business workflow of onboarding a bus company.
        Using database transaction.atomic to ensure atomic reliability.
        """
        code = validated_data.get("code")
        domain = validated_data.get("domain")

        # 1. Enforce unique business constraints
        if self.repository.exists_by_code(code):
            raise ValidationError({"code": f"Tenant code '{code}' is already registered in the system."})
        
        if domain and self.repository.exists_by_domain(domain):
            raise ValidationError({"domain": f"Domain '{domain}' is already linked to another infrastructure."})

        # 2. Automatically map system resource limits aligned to the selected Plan Tier
        plan = validated_data.get("plan", "STANDARD")
        limits = self._resolve_plan_limits(plan)
        validated_data.update(limits)

        # 3. Handle default onboarding timestamps if none provided
        if not validated_data.get("subscription_started_at"):
            validated_data["subscription_started_at"] = timezone.now()
        
        if plan == "TRIAL" and not validated_data.get("subscription_expires_at"):
            # Auto-assign 30 days window for trial environments
            validated_data["subscription_expires_at"] = timezone.now() + timedelta(days=30)

        # 4. Persist data via the repository layer
        tenant = self.repository.create(validated_data)

        # 5. Trigger asynchronous worker tasks (e.g., database seeding, default route provisioning)
        # We pass the ID instead of the object to adhere to Celery serialization best practices.
        transaction.on_commit(lambda: provision_tenant_resources_task.delay(tenant.id))

        return tenant

    def _resolve_plan_limits(self, plan: str) -> dict:
        """Maps system boundaries based on plan tier."""
        plan_matrix = {
            "TRIAL": {"max_users": 3, "max_branches": 1, "max_vehicles": 10},
            "STANDARD": {"max_users": 10, "max_branches": 1, "max_vehicles": 50},
            "PROFESSIONAL": {"max_users": 50, "max_branches": 5, "max_vehicles": 200},
            "ENTERPRISE": {"max_users": 999, "max_branches": 999, "max_vehicles": 9999},
        }
        return plan_matrix.get(plan, plan_matrix["STANDARD"])