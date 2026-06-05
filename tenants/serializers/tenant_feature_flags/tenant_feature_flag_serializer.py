from rest_framework import serializers

from tenants.models.tenent_feature_flag import TenantFeatureFlag


class TenantFeatureFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantFeatureFlag
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")