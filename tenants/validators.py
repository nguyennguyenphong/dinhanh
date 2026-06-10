"""
Centralized validation logic for tenants domain.
"""

import re

from django.core.exceptions import ValidationError


class TenantValidator:
    """Validator cho Tenant domain"""

    @staticmethod
    def validate_code(code: str) -> None:
        """
        Validate tenant code.
        - Must be 3-30 characters
        - Only uppercase letters, numbers, underscores
        """
        if not code or len(code) < 3 or len(code) > 30:
            raise ValidationError("Code phải có 3-30 ký tự")

        if not re.match(r"^[A-Z0-9_]+$", code):
            raise ValidationError("Code chỉ chứa chữ hoa, số và dấu gạch dưới")

    @staticmethod
    def validate_primary_color(color: str) -> None:
        """Validate hex color format"""
        if not re.match(r"^#[0-9A-Fa-f]{6}$", color):
            raise ValidationError("Màu phải ở định dạng hex (#RRGGBB)")

    @staticmethod
    def validate_plan(plan: str) -> None:
        """Validate plan value"""
        from tenants.constants import PLAN_CHOICES

        if plan not in PLAN_CHOICES:
            raise ValidationError(f"Plan phải là một trong: {PLAN_CHOICES}")

    @staticmethod
    def can_add_users(current_users: int, new_users: int, max_users: int) -> bool:
        """Check if can add users within limit"""
        return (current_users + new_users) <= max_users

    @staticmethod
    def can_add_branches(current_branches: int, max_branches: int) -> bool:
        """Check if can add more branches"""
        return current_branches < max_branches
