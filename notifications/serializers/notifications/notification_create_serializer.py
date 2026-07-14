from rest_framework import serializers

from notifications.models.notifications import Notification


class NotificationCreateSerializer(serializers.Serializer):
    tenant_id = serializers.IntegerField(default=1)
    template_id = serializers.IntegerField(required=False, allow_null=True)
    recipient_type = serializers.ChoiceField(choices=Notification.RECIPIENT_TYPE_CHOICES)
    recipient_id = serializers.IntegerField(required=False, allow_null=True)
    recipient_phone = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True)
    recipient_email = serializers.EmailField(max_length=254, required=False, allow_null=True, allow_blank=True)
    channel = serializers.CharField(max_length=20)
    subject = serializers.CharField(max_length=500, required=False, allow_null=True, allow_blank=True)
    body = serializers.CharField()
    ref_type = serializers.CharField(max_length=60, required=False, allow_null=True, allow_blank=True)
    ref_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, attrs):
        from notifications.domain.entities.notification_entity import NotificationEntity
        entity = NotificationEntity(
            id=None,
            tenant_id=attrs.get("tenant_id", 1),
            template_id=attrs.get("template_id"),
            recipient_type=attrs.get("recipient_type", ""),
            recipient_id=attrs.get("recipient_id"),
            recipient_phone=attrs.get("recipient_phone"),
            recipient_email=attrs.get("recipient_email"),
            channel=attrs.get("channel", ""),
            subject=attrs.get("subject"),
            body=attrs.get("body", ""),
            ref_type=attrs.get("ref_type"),
            ref_id=attrs.get("ref_id"),
        )
        try:
            entity.validate()
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        return attrs
