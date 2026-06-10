from rest_framework import serializers


class TenantInvitationAcceptSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=255)
