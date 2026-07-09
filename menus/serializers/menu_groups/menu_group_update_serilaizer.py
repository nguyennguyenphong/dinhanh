from rest_framework import serializers


class MenuGroupUpdateSerializer(serializers.Serializer):
    """Validates data when updating an existing MenuGroup from an edit form."""

    id = serializers.IntegerField(required=True, min_value=1)
    uuid = serializers.UUIDField(required=True)
    code = serializers.CharField(
        required=True,
        min_length=5,
        max_length=50,
        trim_whitespace=True,
        error_messages={
            "required": "Code is required.",
            "min_length": "Code must be at least 5 characters long.",
        },
    )
    label = serializers.CharField(
        required=True,
        max_length=255,
        trim_whitespace=True,
        error_messages={"required": "Label is required."},
    )
    icon = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, default=None
    )
    sort_order = serializers.IntegerField(required=False, default=0)
    is_active = serializers.BooleanField(required=False, default=True)

    def validate_code(self, value: str) -> str:
        """Custom clean rule to ensure updated code is always in lowercase."""
        return value.lower()

    def validate_icon(self, value: str | None) -> str | None:
        if not value:
            return None
        import re

        cleaned_value = value.strip()
        if not re.match(
            r"^<svg.*?>.*?</svg>$", cleaned_value, flags=re.DOTALL | re.IGNORECASE
        ):
            raise serializers.ValidationError(
                "Định dạng icon không hợp lệ. Phải là một thẻ SVG hợp lệ."
            )
        return cleaned_value
