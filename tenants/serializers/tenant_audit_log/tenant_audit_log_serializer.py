from rest_framework import serializers

from tenants.models.tenent_audit_log import TenantAuditLog


class TenantAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantAuditLog
        fields = "__all__"