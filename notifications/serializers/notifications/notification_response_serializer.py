from rest_framework import serializers


class NotificationResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    tenant_id = serializers.IntegerField()
    template_id = serializers.IntegerField(allow_null=True)
    recipient_type = serializers.CharField()
    recipient_id = serializers.IntegerField(allow_null=True)
    recipient_phone = serializers.CharField(allow_null=True)
    recipient_email = serializers.EmailField(allow_null=True)
    channel = serializers.CharField()
    subject = serializers.CharField(allow_null=True)
    body = serializers.CharField()
    status = serializers.CharField()
    retry_count = serializers.IntegerField()
    error_msg = serializers.CharField(allow_null=True)
    ref_type = serializers.CharField(allow_null=True)
    ref_id = serializers.IntegerField(allow_null=True)
    sent_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField(allow_null=True)
    updated_at = serializers.DateTimeField(allow_null=True)
