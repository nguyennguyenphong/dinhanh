from rest_framework import serializers

from notifications.models.notifications import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id",
            "tenant_id",
            "template_id",
            "recipient_type",
            "recipient_id",
            "recipient_phone",
            "recipient_email",
            "channel",
            "subject",
            "body",
            "status",
            "retry_count",
            "error_msg",
            "ref_type",
            "ref_id",
            "sent_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "retry_count",
            "error_msg",
            "sent_at",
            "created_at",
            "updated_at",
        ]

    def validate(self, attrs):
        # Validate entity business logic before creating a notification record
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

    def create(self, validated_data):
        from notifications.providers.notification_provider import NotificationProvider
        from notifications.application.dtos.notifications.notification_create_dto import NotificationCreateDTO
        
        dto = NotificationCreateDTO(
            tenant_id=validated_data["tenant_id"],
            template_id=validated_data.get("template_id"),
            recipient_type=validated_data["recipient_type"],
            recipient_id=validated_data.get("recipient_id"),
            recipient_phone=validated_data.get("recipient_phone"),
            recipient_email=validated_data.get("recipient_email"),
            channel=validated_data["channel"],
            subject=validated_data.get("subject"),
            body=validated_data["body"],
            ref_type=validated_data.get("ref_type"),
            ref_id=validated_data.get("ref_id"),
        )
        
        response = NotificationProvider.create_notification().execute(dto)
        return Notification.objects.get(pk=response.id)
