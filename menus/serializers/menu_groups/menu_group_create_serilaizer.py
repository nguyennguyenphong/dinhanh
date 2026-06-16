"""
Serializers for MenuGroup data validation and parsing.
Used to strictly validate incoming HTML Form data before converting into DTOs.
"""

from __future__ import annotations

from rest_framework import serializers

import re


class MenuGroupCreateSerializer(serializers.Serializer):
    """Validates data when creating a new MenuGroup from a Form."""

    tenant = serializers.IntegerField(
        required=True,
        min_value=1,
        error_messages={"min_value": "Invalid tenant. Must be a positive integer."},
    )
    code = serializers.CharField(
        required=True,
        min_length=5,
        max_length=50,
        trim_whitespace=True,
        error_messages={
            "required": "Code is required.",
            "min_length": "Code must be at least 5 characters long.",
        },
    )
    label = serializers.CharField(
        required=True,
        max_length=255,
        trim_whitespace=True,
        error_messages={"required": "Label is required."},
    )
    icon = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, default=None, min_length=5
    )
    sort_order = serializers.IntegerField(required=False, default=0)
    is_active = serializers.BooleanField(required=False, default=True)

    """Validate code"""
    def validate_code(self, value: str) -> str:
        """Custom clean rule to ensure code is strictly stored in lowercase format."""
        return value.lower()

    """Validate icon (svg tag format)"""
    def validate_icon(self, value: str | None) -> str | None:

        if not value:
            return None
            
        cleaned_value = value.strip()
        
        if not re.match(r"^<svg.*?>.*?</svg>$", cleaned_value, flags=re.DOTALL | re.IGNORECASE):
            raise serializers.ValidationError("Icon format is invalid. It must be a valid SVG tag.")
            
        return cleaned_value

    """General validate"""
    def validate(self, attrs: dict) -> dict:
        tenant_id = attrs.get("tenant")
        code = attrs.get("code")
        sort_order = attrs.get("sort_order")

        repo = self.context.get("menu_group_repo")
        
        if not repo:
            return attrs

        if tenant_id and code:
            if repo.exists_by_code(tenant=tenant_id, code=code):
                raise serializers.ValidationError({
                    "code": f"Menu group code '{code}' already exists for this tenant."
                })

        if tenant_id and sort_order is not None:
            if hasattr(repo, "exists_by_sort_order") and repo.exists_by_sort_order(tenant=tenant_id, sort_order=sort_order):
                raise serializers.ValidationError({
                    "sort_order": f"Sort order {sort_order} is already taken within this tenant."
                })

        return attrs
