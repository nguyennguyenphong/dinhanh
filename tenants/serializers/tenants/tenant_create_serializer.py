from rest_framework import serializers

from tenants.models.tenants import Tenant

class TenantCreateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=30)
    name = serializers.CharField(max_length=255)
    plan = serializers.ChoiceField(choices=Tenant.PLAN_CHOICES, default="STANDARD")
    domain = serializers.CharField(max_length=255, required=False, allow_null=True)
    logo_url = serializers.URLField(max_length=500, required=False, allow_null=True)
    primary_color = serializers.CharField(max_length=7, default="#3B82F6")
    currency = serializers.ChoiceField(choices=Tenant.CURRENCY_CHOICES, default="VND")
    exchange_rate = serializers.DecimalField(max_digits=12, decimal_places=4, default=1.0000)
    default_language = serializers.ChoiceField(choices=Tenant.LANGUAGE_CHOICES, default="vi")
    timezone = serializers.ChoiceField(choices=Tenant.TIMEZONE_CHOICES, default="Asia/Ho_Chi_Minh")
    subscription_days = serializers.IntegerField(default=30, min_value=1)
    settings = serializers.JSONField(default=dict, required=False)