from rest_framework import serializers


class NotificationTemplateResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tenant_id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()
    channel = serializers.CharField()
    subject = serializers.CharField(allow_null=True)
    body = serializers.CharField()
    variables = serializers.ListField(child=serializers.CharField())
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField(allow_null=True)
    updated_at = serializers.DateTimeField(allow_null=True)
