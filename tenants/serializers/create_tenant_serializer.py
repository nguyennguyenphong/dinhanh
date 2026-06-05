# ============================================================================
# FILE: tenants/serializers/create_tenant_Serializer.py
# Request Validators / Serializers for Tenant Model
# ============================================================================

from decimal import Decimal
from django.core.validators import RegexValidator, URLValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from tenants.models.tenants import Tenant


class TenantRequestSerializer(serializers.ModelSerializer):
    """
    Enterprise-grade validator and serializer for the Tenant model.
    Handles strict data sanitization, custom business logic, and security checks.
    """

    # Strict validation for Unique fields to prevent race conditions at database level
    code = serializers.CharField(
        max_length=30,
        required=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z0-9_]+$",
                message="Code must contain only uppercase letters, numbers, and underscores.",
            ),
            UniqueValidator(
                queryset=Tenant.objects.all(),
                lookup="iexact",
                message="A tenant with this code already exists.",
            ),
        ],
    )

    domain = serializers.CharField(
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True,
        validators=[
            URLValidator(message="Enter a valid custom domain URL."),
            UniqueValidator(
                queryset=Tenant.objects.all(),
                message="This custom domain is already assigned to another tenant.",
            ),
        ],
    )

    exchange_rate = serializers.DecimalField(
        max_digits=12,
        decimal_places=4,
        required=False,
        min_value=Decimal("0.0001"),
        error_messages={
            "min_value": "Exchange rate must be a positive value greater than 0.",
        },
    )

    class Meta:
        model = Tenant
        fields = [
            "id",
            "uuid",
            "code",
            "name",
            "domain",
            "logo_url",
            "primary_color",
            "plan",
            "currency",
            "exchange_rate",
            "default_language",
            "timezone",
            "is_active",
            "settings",
            "subscription_started_at",
            "subscription_expires_at",
            "max_users",
            "max_branches",
            "max_vehicles",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]

    # ============================================================================
    # Field-Level Validators (clean_<field> equivalent in Django Forms)
    # ============================================================================

    def validate_name(self, value):
        """Sanitize and validate tenant name."""
        stripped_value = value.strip() if value else ""
        if len(stripped_value) < 3:
            raise serializers.ValidationError("Tenant name must be at least 3 characters long.")
        return stripped_value

    def validate_settings(self, value):
        """Ensure settings block does not contain malicious injected or corrupted JSON structures."""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Settings must be a valid JSON object structure.")
        return value

    # ============================================================================
    # Object-Level/Cross-Field Validators (clean() equivalent in Django Forms)
    # ============================================================================

    def validate(self, attrs):
        """
        Cross-field complex enterprise business logic validations.
        Executes on both POST (Create) and PATCH (Partial Update).
        """
        # Extract existing instance state for PATCH/PUT operations
        instance = self.instance

        # 1. Fallback mechanisms to handle partial updates seamlessly
        subscription_started_at = attrs.get(
            "subscription_started_at", 
            getattr(instance, "subscription_started_at", None)
        )
        subscription_expires_at = attrs.get(
            "subscription_expires_at", 
            getattr(instance, "subscription_expires_at", None)
        )
        plan = attrs.get("plan", getattr(instance, "plan", "STANDARD"))
        max_users = attrs.get("max_users", getattr(instance, "max_users", 10))
        max_branches = attrs.get("max_branches", getattr(instance, "max_branches", 1))
        max_vehicles = attrs.get("max_vehicles", getattr(instance, "max_vehicles", 50))

        # 2. Business Rule: Chronological order validation for subscriptions
        if subscription_started_at and subscription_expires_at:
            if subscription_started_at >= subscription_expires_at:
                raise serializers.ValidationError(
                    {
                        "subscription_expires_at": (
                            "Subscription expiration date must be strictly after the start date."
                        )
                    }
                )

        # 3. Business Rule: Strict validation of subscription dates based on plan type
        if plan == "TRIAL" and not subscription_expires_at:
            raise serializers.ValidationError(
                {"subscription_expires_at": "Trial plans require an explicit expiration date setting."}
            )

        # 4. Business Rule: Enforce resource boundary limits matching the selected Tier Plan
        # This prevents privilege escalation or unauthorized system resource consumption via API payload manipulation.
        features = self._get_plan_limits(plan)
        if features:
            errors = {}
            if max_users > features["max_users"]:
                errors["max_users"] = f"Max users for tier '{plan}' cannot exceed {features['max_users']}."
            if max_branches > features["max_branches"]:
                errors["max_branches"] = f"Max branches for tier '{plan}' cannot exceed {features['max_branches']}."
            if max_vehicles > features["max_vehicles"]:
                errors["max_vehicles"] = f"Max vehicles for tier '{plan}' cannot exceed {features['max_vehicles']}."
            
            if errors:
                raise serializers.ValidationError(errors)

        return attrs

    def _get_plan_limits(self, plan):
        """Helper method hosting rigid threshold constraints per service level tier."""
        limits = {
            "TRIAL": {"max_users": 3, "max_branches": 1, "max_vehicles": 10},
            "STANDARD": {"max_users": 10, "max_branches": 1, "max_vehicles": 50},
            "PROFESSIONAL": {"max_users": 50, "max_branches": 5, "max_vehicles": 200},
            "ENTERPRISE": {"max_users": 999, "max_branches": 999, "max_vehicles": 9999},
        }
        return limits.get(plan, {})