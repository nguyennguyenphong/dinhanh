# ============================================================================
# FILE: apps/tenants/dtos/tenant_dto.py
# ============================================================================
from rest_framework import serializers
from decimal import Decimal
from django.core.validators import RegexValidator

class TenantCreateDTO(serializers.Serializer):
    """
    DTO for validating inbound payload when creating a new Tenant.
    Acts as the strict contract between the client and our service layer.
    """
    code = serializers.CharField(
        max_length=30,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9_]+$",
                message="Code must contain only uppercase letters, numbers, and underscores.",
            )
        ]
    )
    name = serializers.CharField(max_length=255)
    domain = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    logo_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    primary_color = serializers.CharField(max_length=7, default="#3B82F6")
    plan = serializers.ChoiceField(choices=["TRIAL", "STANDARD", "PROFESSIONAL", "ENTERPRISE"], default="STANDARD")
    currency = serializers.CharField(max_length=10, default="VND")
    exchange_rate = serializers.DecimalField(max_digits=12, decimal_places=4, default=Decimal("1.0000"))
    default_language = serializers.CharField(max_length=10, default="vi")
    timezone = serializers.CharField(max_length=50, default="Asia/Ho_Chi_Minh")
    settings = serializers.JSONField(required=False, default=dict)
    
    # Subscription info (optional during onboarding initialization)
    subscription_started_at = serializers.DateTimeField(required=False, allow_null=True)
    subscription_expires_at = serializers.DateTimeField(required=False, allow_null=True)

    def validate_code(self, value):
        """Upper casing the code for consistency."""
        return value.strip().upper()

    def validate(self, attrs):
        """Cross-field business logic validations before passing to Service."""
        start = attrs.get("subscription_started_at")
        end = attrs.get("subscription_expires_at")
        if start and end and start >= end:
            raise serializers.ValidationError({"subscription_expires_at": "Expiration date must be after start date."})
        return attrs