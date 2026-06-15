from __future__ import annotations

from rest_framework import serializers


class MenuGroupSoftDeleteSerializer(serializers.Serializer):
    """Validates constraints prior to moving a record to the safe trash bin."""

    id = serializers.IntegerField(required=True, min_value=1)
    tenant_id = serializers.IntegerField(required=True, min_value=1)