# ============================================================================
# FILE: tenants/tests/test_tenant_creation.py
# ============================================================================
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class TenantProvisioningTests(APITestCase):
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="saas_admin", email="admin@cms.com", password="SecurePassword123"
        )
        self.url = reverse("tenant-provision")

    def test_admin_can_successfully_create_valid_tenant(self):
        """Verify explicit system rules match performance specifications."""
        self.client.force_authenticate(user=self.admin_user)
        payload = {
            "code": "ALPHABUS",
            "name": "Alpha Express Transport LLC",
            "plan": "PROFESSIONAL",
            "currency": "VND",
            "timezone": "Asia/Ho_Chi_Minh"
        }
        response = self.client.post(self.url, payload, format="json")
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["code"], "ALPHABUS")
        
        # Ensure underlying limits were attached correctly by service tier injection
        from tenants.models.tenants import Tenant
        tenant = Tenant.objects.get(code="ALPHABUS")
        self.assertEqual(tenant.max_vehicles, 200) # Max vehicles for PROFESSIONAL tier