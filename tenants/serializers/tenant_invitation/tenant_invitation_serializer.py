from rest_framework import serializers

from tenants.models.tenent_invitation import TenantInvitation

class TenantInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantInvitation
        fields = '__all__'
        read_only_fields = ('id', 'token', 'created_at')