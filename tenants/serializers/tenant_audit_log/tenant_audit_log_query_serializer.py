from rest_framework import serializers


class TenantAuditLogQuerySerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=["CREATE", "UPDATE", "DELETE", "LOGIN", "EXPORT"],
        required=False,
    )
    module = serializers.CharField(required=False, allow_blank=True)
    limit = serializers.IntegerField(min_value=1, max_value=200, default=50)
    offset = serializers.IntegerField(min_value=0, default=0)
