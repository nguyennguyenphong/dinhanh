from __future__ import annotations

from rest_framework import serializers
from menus.models import MenuItem, MenuItemRole
from accounts.models.roles import Role


class MenuItemRoleCreateSerializer(serializers.Serializer):
    """Validates data when assigning a Role to a MenuItem."""

    menu_item = serializers.IntegerField(
        required=True,
        error_messages={"required": "Menu item is required."},
    )
    role = serializers.IntegerField(
        required=True,
        error_messages={"required": "Role is required."},
    )

    def validate(self, attrs: dict) -> dict:
        menu_item_id = attrs.get("menu_item")
        role_id = attrs.get("role")

        # 1. Check if menu item exists
        menu_item = MenuItem.objects.filter(pk=menu_item_id).first()
        if not menu_item:
            raise serializers.ValidationError({"menu_item": "Menu item does not exist."})

        # 2. Check if role exists
        role = Role.objects.filter(pk=role_id).first()
        if not role:
            raise serializers.ValidationError({"role": "Role does not exist."})

        # 3. Check tenant consistency
        if menu_item.tenant_id != role.tenant_id:
            raise serializers.ValidationError(
                "Menu item and role must belong to the same tenant."
            )

        # 4. Check if already assigned
        if MenuItemRole.objects.filter(menu_item_id=menu_item_id, role_id=role_id).exists():
            raise serializers.ValidationError(
                "This role is already assigned to this menu item."
            )

        return attrs
