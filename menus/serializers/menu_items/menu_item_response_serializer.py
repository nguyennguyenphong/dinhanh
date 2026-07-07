from rest_framework import serializers


class MenuItemResponseSerializer(serializers.Serializer):
    """Serializer for MenuItem response data."""

    id = serializers.IntegerField()
    uuid = serializers.CharField()
    tenant_id = serializers.IntegerField()
    group_id = serializers.IntegerField(allow_null=True)
    parent_id = serializers.IntegerField(allow_null=True)
    code = serializers.CharField()
    label = serializers.CharField()
    url_name = serializers.CharField(allow_null=True, allow_blank=True)
    url_path = serializers.CharField(allow_null=True, allow_blank=True)
    icon = serializers.CharField(allow_null=True, allow_blank=True)
    badge_text = serializers.CharField(allow_null=True, allow_blank=True)
    permission_code = serializers.CharField(allow_null=True, allow_blank=True)
    sort_order = serializers.IntegerField()
    open_in_new_tab = serializers.BooleanField()
    is_active = serializers.BooleanField()
    is_hidden = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
