from rest_framework import serializers


class MenuItemRoleResponseSerializer(serializers.Serializer):
    """Serializer for MenuItemRole response data."""

    id = serializers.IntegerField()
    uuid = serializers.CharField()
    menu_item_id = serializers.IntegerField()
    role_id = serializers.IntegerField()
    tenant_id = serializers.IntegerField()
