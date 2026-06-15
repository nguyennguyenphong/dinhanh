from __future__ import annotations

from rest_framework import serializers

class MenuGroupHardDeleteSerializer(serializers.Serializer):
    """Validates constraints prior to physically wiping a record permanently."""

    id = serializers.IntegerField(required=True, min_value=1)
    tenant_id = serializers.IntegerField(required=True, min_value=1)