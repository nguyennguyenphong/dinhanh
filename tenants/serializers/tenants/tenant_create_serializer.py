from rest_framework import serializers

from tenants.models.tenants import Tenant


class TenantCreateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=30)
    name = serializers.CharField(max_length=255)

    domain = serializers.CharField(
        max_length=255,
        required=False,
        allow_null=True,
        allow_blank=True
    )

    logo_url = serializers.URLField(
        max_length=500,
        required=False,
        allow_null=True
    )

    primary_color = serializers.CharField(
        max_length=7,
        default="#3B82F6"
    )

    plan = serializers.ChoiceField(
        choices=Tenant.PLAN_CHOICES,
        default="STANDARD"
    )

    currency = serializers.ChoiceField(
        choices=Tenant.CURRENCY_CHOICES,
        default="VND"
    )

    exchange_rate = serializers.DecimalField(
        max_digits=12,
        decimal_places=4,
        default=1.0000
    )

    default_language = serializers.ChoiceField(
        choices=Tenant.LANGUAGE_CHOICES,
        default="vi"
    )

    timezone = serializers.ChoiceField(
        choices=Tenant.TIMEZONE_CHOICES,
        default="Asia/Ho_Chi_Minh"
    )

    is_active = serializers.BooleanField(default=True)

    settings = serializers.JSONField(
        default=dict,
        required=False
    )

    subscription_started_at = serializers.DateTimeField(
        required=False,
        allow_null=True
    )

    subscription_ended_at = serializers.DateTimeField(
        required=False,
        allow_null=True
    )

    max_users = serializers.IntegerField(
        required=False,
        allow_null=False,
        default=10
    )

    max_branches = serializers.IntegerField(
        required=False,
        allow_null=False,
        default=1
    )

    max_vehicles = serializers.IntegerField(
        required=False,
        allow_null=False,
        default=50
    )

    def validate_code(self, value):
        if Tenant.objects.filter(code=value).exists():
            raise serializers.ValidationError(
                "Mã tenant đã tồn tại."
            )

        return value

    def validate_domain(self, value):
        if not value:
            return value

        if not value.startswith("https://"):
            raise serializers.ValidationError(
                "Domain phải bắt đầu bằng https://"
            )

        return value

    def validate(self, attrs):
        started_at = attrs.get("subscription_started_at")
        ended_at = attrs.get("subscription_ended_at")

        if (
            started_at
            and ended_at
            and started_at >= ended_at
        ):
            raise serializers.ValidationError({
                "subscription_ended_at":
                    "Ngày kết thúc phải lớn hơn ngày bắt đầu."
            })

        return attrs