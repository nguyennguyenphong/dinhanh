from rest_framework import serializers
from tenants.models.tenants import Tenant


class TenantSerializer(serializers.ModelSerializer):
    is_trial_expired = serializers.SerializerMethodField()
    is_subscription_active = serializers.SerializerMethodField()
    plan_features = serializers.SerializerMethodField()

    class Meta:
        model = Tenant
        fields = '__all__'
        read_only_fields = ('id', 'uuid', 'created_at', 'updated_at')

    def get_is_trial_expired(self, obj) -> bool:
        return obj.is_trial_expired()

    def get_is_subscription_active(self, obj) -> bool:
        return obj.is_subscription_active()

    def get_plan_features(self, obj) -> dict:
        return obj.get_plan_features()