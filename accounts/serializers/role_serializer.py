from rest_framework import serializers


class RoleSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tenant_id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    description = serializers.CharField(allow_null=True)
    is_system = serializers.BooleanField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField(allow_null=True)
    updated_at = serializers.DateTimeField(allow_null=True)


class RoleListQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    limit = serializers.IntegerField(min_value=1, max_value=200, default=20)
    offset = serializers.IntegerField(min_value=0, default=0)


class RoleCreateSerializer(serializers.Serializer):
    tenant = serializers.IntegerField()
    name = serializers.CharField(max_length=100)
    slug = serializers.CharField(max_length=100, required=False, allow_blank=True)
    description = serializers.CharField(
        max_length=1000, required=False, allow_null=True, allow_blank=True
    )
    is_active = serializers.BooleanField(default=True)


class RoleUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    slug = serializers.CharField(max_length=100)
    description = serializers.CharField(
        max_length=1000, required=False, allow_null=True, allow_blank=True
    )
    is_active = serializers.BooleanField(default=True)
