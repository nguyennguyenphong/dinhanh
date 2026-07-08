from rest_framework import serializers


class AssetListQuerySerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(
        choices=["IN_USE", "MAINTENANCE", "DISPOSED", "LOST", "TRANSFERRED"],
        required=False,
        allow_blank=True,
    )
    category_id = serializers.IntegerField(required=False, allow_null=True)
    branch_id = serializers.IntegerField(required=False, allow_null=True)
    ordering = serializers.CharField(required=False, default="-created_at")
    limit = serializers.IntegerField(min_value=1, max_value=200, default=20)
    offset = serializers.IntegerField(min_value=0, default=0)

    def validate_ordering(self, value: str) -> list[str]:
        allowed = {
            "created_at",
            "-created_at",
            "name",
            "-name",
            "code",
            "-code",
            "purchase_price",
            "-purchase_price",
        }
        parts = [p.strip() for p in value.split(",") if p.strip()]
        invalid = [p for p in parts if p not in allowed]
        if invalid:
            raise serializers.ValidationError(
                f"Invalid ordering fields: {invalid}. Allowed: {sorted(allowed)}"
            )
        return parts
