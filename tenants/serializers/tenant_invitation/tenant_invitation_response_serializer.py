from rest_framework import serializers


class TenantInvitationResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tenant_id = serializers.IntegerField()
    email = serializers.EmailField()
    status = serializers.CharField()
    invited_by_id = serializers.IntegerField()
    expires_at = serializers.DateTimeField()
    accepted_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField(allow_null=True)
