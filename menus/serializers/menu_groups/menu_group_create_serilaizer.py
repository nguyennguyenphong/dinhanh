"""
Serializers for MenuGroup data validation and parsing.
Used to strictly validate incoming HTML Form data before converting into DTOs.
"""

from __future__ import annotations

from rest_framework import serializers


class MenuGroupCreateSerializer(serializers.Serializer):
    """Validates data when creating a new MenuGroup from a Form."""

    tenant_id = serializers.IntegerField(
        required=True, 
        min_value=1,
        error_messages={"min_value": "Invalid tenant_id. Must be a positive integer."}
    )
    code = serializers.CharField(
        required=True,
        min_length=5,
        max_length=50,
        trim_whitespace=True,
        error_messages={
            "required": "Code is required.",
            "min_length": "Code must be at least 5 characters long."
        }
    )
    label = serializers.CharField(
        required=True,
        max_length=255,
        trim_whitespace=True,
        error_messages={"required": "Label is required."}
    )
    icon = serializers.CharField(
        required=False, 
        allow_null=True, 
        allow_blank=True, 
        default=None,
        max_length=255
    )
    sort_order = serializers.IntegerField(
        required=False, 
        default=0
    )
    is_active = serializers.BooleanField(
        required=False, 
        default=True
    )

    def validate_code(self, value: str) -> str:
        """Custom clean rule to ensure code is strictly stored in lowercase format."""
        return value.lower()
