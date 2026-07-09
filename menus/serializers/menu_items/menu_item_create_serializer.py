from __future__ import annotations

from rest_framework import serializers

from menus.models.menu_groups import MenuGroup
from menus.models.menu_items import MenuItem


class MenuItemCreateSerializer(serializers.Serializer):
    """Validates data when creating a new MenuItem from a Form."""

    tenant = serializers.IntegerField(
        required=True,
        min_value=1,
        error_messages={"min_value": "Invalid tenant ID. Must be positive."},
    )
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

    def validate_icon(self, value: str | None) -> str | None:
        if not value:
            return None
        import re

        cleaned_value = value.strip()
        if not re.match(
            r"^<svg.*?>.*?</svg>$", cleaned_value, flags=re.DOTALL | re.IGNORECASE
        ):
            raise serializers.ValidationError(
                "Định dạng icon không hợp lệ. Phải là một thẻ SVG hợp lệ."
            )
        return cleaned_value

    def validate(self, attrs: dict) -> dict:
        tenant_id = attrs.get("tenant")
        code = attrs.get("code")
        group_id = attrs.get("group_id")
        parent_id = attrs.get("parent_id")
        url_name = attrs.get("url_name")
        url_path = attrs.get("url_path")

        # 1. Check uniqueness of code
        repo = self.context.get("menu_item_repo")
        if repo and tenant_id and code:
            if repo.exists_with_code(tenant_id=tenant_id, code=code):
                raise serializers.ValidationError(
                    {"code": f"Menu item code '{code}' already exists for this tenant."}
                )

        # 2. Check at least one URL strategy is defined
        if not url_name and not url_path:
            raise serializers.ValidationError(
                "Either url_name or url_path must be provided."
            )

        # 3. Check group tenant alignment
        if group_id and tenant_id:
            group = MenuGroup.objects.filter(pk=group_id).first()
            if not group or group.tenant_id != tenant_id:
                raise serializers.ValidationError(
                    {"group_id": "Specified menu group must belong to the same tenant."}
                )

        # 4. Check parent tenant alignment
        if parent_id and tenant_id:
            parent = MenuItem.objects.filter(pk=parent_id).first()
            if not parent or parent.tenant_id != tenant_id:
                raise serializers.ValidationError(
                    {"parent_id": "Parent menu item must belong to the same tenant."}
                )

        return attrs
