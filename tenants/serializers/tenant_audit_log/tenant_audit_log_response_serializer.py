from rest_framework import serializers


class TenantAuditLogResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    user_id = serializers.IntegerField(allow_null=True)
    username = serializers.CharField(allow_null=True)
    action = serializers.CharField()
    module = serializers.CharField()
    object_type = serializers.CharField(allow_null=True)
    object_id = serializers.CharField(allow_null=True)
    object_repr = serializers.CharField(allow_null=True)
    old_values = serializers.DictField(allow_null=True)
    new_values = serializers.DictField(allow_null=True)
    changes = serializers.DictField(allow_null=True)
    ip_address = serializers.IPAddressField(allow_null=True)
    status = serializers.CharField()
    error_message = serializers.CharField(allow_null=True)
    created_at = serializers.DateTimeField()