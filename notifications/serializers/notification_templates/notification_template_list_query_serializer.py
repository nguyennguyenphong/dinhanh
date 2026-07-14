from rest_framework import serializers


class NotificationTemplateListQuerySerializer(serializers.Serializer):
    tenant_id = serializers.IntegerField(required=False)
    channel = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False, allow_null=True)
    search = serializers.CharField(required=False, allow_blank=True)
    ordering = serializers.CharField(required=False, default="-created_at")
    limit = serializers.IntegerField(min_value=1, max_value=200, default=20)
    offset = serializers.IntegerField(min_value=0, default=0)

    def validate_ordering(self, value: str) -> list[str]:
        allowed = {"created_at", "-created_at", "code", "-code", "channel", "-channel"}
        parts = [p.strip() for p in value.split(",") if p.strip()]
        invalid = [p for p in parts if p not in allowed]
        if invalid:
            raise serializers.ValidationError(
                f"Invalid ordering fields: {invalid}. Allowed: {sorted(allowed)}"
            )
        return parts
