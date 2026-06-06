from rest_framework import serializers


class TenantInvitationCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    expires_in_days = serializers.IntegerField(min_value=1, max_value=30, default=7)