from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from tenants.models.tenants import Tenant

User = get_user_model()

class TenantEnterpriseLifecycleTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        # Prepare execution actors mockups
        self.superuser = User.objects.create_superuser(
            username="globaladmin", email="admin@saas.com", password="SecurePassword123"
        )
        self.client.force_authenticate(user=self.superuser)
        
        # Preseed execution entry points baseline configurations
        self.existing_tenant = Tenant.objects.create(
            code="TAXI_PHUONGTRANG",
            name="Phuong Trang Bus Lines",
            plan="ENTERPRISE",
            is_active=True
        )

    def test_create_tenant_valid_payload(self):
        payload = {
            "code": "ALOHA_EXPRESS",
            "name": "Aloha Express Services",
            "plan": "STANDARD",
            "currency": "USD",
            "max_users": 20
        }
        response = self.client.post("/api/tenants/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["code"], "ALOHA_EXPRESS")
        
    def test_list_tenants_success(self):
        response = self.client.get("/api/tenants/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) >= 1)

    def test_update_tenant_partial(self):
        payload = {"name": "Phuong Trang Transport Group"}
        url = f"/api/tenants/{self.existing_tenant.id}/"
        response = self.client.put(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Phuong Trang Transport Group")

    def test_delete_tenant_action(self):
        url = f"/api/tenants/{self.existing_tenant.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)