from rest_framework import serializers


class PermissionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tenant_id = serializers.IntegerField()
    codename = serializers.CharField()
    name = serializers.CharField()
    module = serializers.CharField()
    action = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    parent_id = serializers.IntegerField(allow_null=True)
    is_active = serializers.BooleanField()
    is_system = serializers.BooleanField()
    created_at = serializers.DateTimeField(allow_null=True)
    updated_at = serializers.DateTimeField(allow_null=True)


class PermissionListQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    limit = serializers.IntegerField(min_value=1, max_value=200, default=20)
    offset = serializers.IntegerField(min_value=0, default=0)
