from rest_framework import serializers


class MenuGroupResponseSerializer(serializers.Serializer):
    """Serializer for MenuGroup response data."""

    id = serializers.IntegerField()
    uuid = serializers.CharField()
    tenant_id = serializers.IntegerField()
    code = serializers.CharField()
    label = serializers.CharField()
    icon = serializers.CharField(allow_null=True, allow_blank=True)
    sort_order = serializers.IntegerField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
