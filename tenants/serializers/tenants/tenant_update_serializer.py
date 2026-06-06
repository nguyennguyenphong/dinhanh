from rest_framework import serializers


class TenantUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    plan = serializers.ChoiceField(
        choices=["TRIAL", "STANDARD", "PROFESSIONAL", "ENTERPRISE"],
        required=False,
    )
    currency = serializers.ChoiceField(
        choices=["VND", "USD", "EUR", "LAK", "KHR"],
        required=False,
    )
    exchange_rate = serializers.DecimalField(
        max_digits=12, decimal_places=4, required=False
    )
    default_language = serializers.ChoiceField(
        choices=["vi", "en", "lo", "km"], required=False
    )
    timezone = serializers.ChoiceField(
        choices=[
            "Asia/Ho_Chi_Minh",
            "Asia/Vientiane",
            "Asia/Phnom_Penh",
            "Asia/Bangkok",
        ],
        required=False,
    )
    primary_color = serializers.RegexField(
        regex=r"^#[0-9A-Fa-f]{6}$", max_length=7, required=False
    )
    domain = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    logo_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    max_users = serializers.IntegerField(min_value=1, required=False)
    max_branches = serializers.IntegerField(min_value=1, required=False)
    max_vehicles = serializers.IntegerField(min_value=1, required=False)
    subscription_started_at = serializers.DateTimeField(required=False, allow_null=True)
    subscription_expires_at = serializers.DateTimeField(required=False, allow_null=True)
    settings = serializers.DictField(required=False)