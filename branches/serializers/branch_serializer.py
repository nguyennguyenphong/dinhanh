from rest_framework import serializers


class BranchSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tenant_id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()
    address = serializers.CharField(allow_null=True)
    phone = serializers.CharField(allow_null=True)
    email = serializers.CharField(allow_null=True)
    manager_id = serializers.IntegerField(allow_null=True)
    latitude = serializers.DecimalField(
        max_digits=10, decimal_places=7, allow_null=True
    )
    longitude = serializers.DecimalField(
        max_digits=10, decimal_places=7, allow_null=True
    )
    timezone = serializers.CharField()
    is_active = serializers.BooleanField()
    metadata = serializers.JSONField(default=dict)
    created_at = serializers.DateTimeField(allow_null=True)
    updated_at = serializers.DateTimeField(allow_null=True)


class BranchListQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    limit = serializers.IntegerField(min_value=1, max_value=200, default=20)
    offset = serializers.IntegerField(min_value=0, default=0)
