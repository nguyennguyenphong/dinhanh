from __future__ import annotations

import uuid
from rest_framework import serializers

from menus.models.menu_groups import MenuGroup
from menus.models.menu_items import MenuItem


class MenuItemUpdateSerializer(serializers.Serializer):
    """Validates data when updating an existing MenuItem from an edit form."""

    id = serializers.IntegerField(required=True, min_value=1)
    uuid = serializers.UUIDField(required=True)
    code = serializers.CharField(
        required=True,
        min_length=3,
        max_length=80,
        trim_whitespace=True,
        error_messages={
            "required": "Code is required.",
            "min_length": "Code must be at least 3 characters long.",
        },
    )
    label = serializers.CharField(
        required=True,
        max_length=150,
        trim_whitespace=True,
        error_messages={"required": "Label is required."},
    )
    group_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    parent_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    url_name = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, default=None, max_length=150
    )
    url_path = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, default=None, max_length=300
    )
    icon = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, default=None
    )
    badge = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, default=None, max_length=30
    )
    permission_code = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, default=None, max_length=150
    )
    sort_order = serializers.IntegerField(required=False, default=0)
    open_in_new_tab = serializers.BooleanField(required=False, default=False)
    is_active = serializers.BooleanField(required=False, default=True)
    is_hidden = serializers.BooleanField(required=False, default=False)

    def validate_code(self, value: str) -> str:
        """Ensure code is strictly in lowercase format."""
        return value.lower()

    def validate(self, attrs: dict) -> dict:
        item_id = attrs.get("id")
        code = attrs.get("code")
        group_id = attrs.get("group_id")
        parent_id = attrs.get("parent_id")
        url_name = attrs.get("url_name")
        url_path = attrs.get("url_path")

        # 1. Fetch current MenuItem model to check tenant boundaries
        menu_item_model = MenuItem.objects.filter(pk=item_id).first()
        if not menu_item_model:
            raise serializers.ValidationError({"id": "Menu item does not exist."})

        tenant_id = menu_item_model.tenant_id

        # 2. Check uniqueness of code
        repo = self.context.get("menu_item_repo")
        if repo and code:
            if repo.exists_with_code(
                tenant_id=tenant_id, code=code, exclude_id=item_id
            ):
                raise serializers.ValidationError(
                    {"code": f"Menu item code '{code}' already exists for this tenant."}
                )

        # 3. Check at least one URL strategy is defined
        if not url_name and not url_path:
            raise serializers.ValidationError(
                "Either url_name or url_path must be provided."
            )

        # 4. Check group tenant alignment
        if group_id:
            group = MenuGroup.objects.filter(pk=group_id).first()
            if not group or group.tenant_id != tenant_id:
                raise serializers.ValidationError(
                    {"group_id": "Specified menu group must belong to the same tenant."}
                )

        # 5. Check parent tenant alignment
        if parent_id:
            if parent_id == item_id:
                raise serializers.ValidationError(
                    {"parent_id": "Menu item cannot be its own parent."}
                )
            parent = MenuItem.objects.filter(pk=parent_id).first()
            if not parent or parent.tenant_id != tenant_id:
                raise serializers.ValidationError(
                    {"parent_id": "Parent menu item must belong to the same tenant."}
                )

        return attrs
