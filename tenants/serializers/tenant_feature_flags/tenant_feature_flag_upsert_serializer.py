from rest_framework import serializers


class TenantFeatureFlagUpsertSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    is_enabled = serializers.BooleanField()
    rollout_percentage = serializers.IntegerField(min_value=0, max_value=100, default=100)
    config = serializers.DictField(required=False, default=dict)
 
    def validate_code(self, value: str) -> str:
        return value.upper().strip()