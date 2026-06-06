from rest_framework import serializers


class TenantFeatureFlagResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tenant_id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    is_enabled = serializers.BooleanField()
    rollout_percentage = serializers.IntegerField()
    config = serializers.DictField()
    created_at = serializers.DateTimeField(allow_null=True)
    updated_at = serializers.DateTimeField(allow_null=True)