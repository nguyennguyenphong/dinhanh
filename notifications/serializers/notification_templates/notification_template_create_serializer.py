import re

from rest_framework import serializers

from notifications.models.notification_templates import NotificationTemplate


class NotificationTemplateCreateSerializer(serializers.Serializer):
    tenant_id = serializers.IntegerField()
    code = serializers.CharField(max_length=50)
    name = serializers.CharField(max_length=255)
    channel = serializers.ChoiceField(choices=NotificationTemplate.CHANNEL_CHOICES)
    subject = serializers.CharField(
        max_length=500, required=False, allow_null=True, allow_blank=True
    )
    body = serializers.CharField()
    variables = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    is_active = serializers.BooleanField(default=True)

    def validate_code(self, value):
        return value.upper().strip()

    def validate(self, attrs):
        tenant_id = attrs.get("tenant_id")
        code = attrs.get("code")
        channel = attrs.get("channel")

        from notifications.providers.notification_provider import NotificationProvider

        if (
            NotificationProvider.get_template()
            ._template_repo()
            .exists_by_code_channel(tenant_id=tenant_id, code=code, channel=channel)
        ):
            raise serializers.ValidationError(
                {
                    "code": f"Template with code '{code}' and channel '{channel}' already exists for this tenant."
                }
            )

        # Domain level validations
        from notifications.domain.entities.notification_template_entity import (
            NotificationTemplateEntity,
        )

        entity = NotificationTemplateEntity(
            id=None,
            tenant_id=tenant_id,
            code=code,
            name=attrs.get("name", ""),
            channel=channel,
            subject=attrs.get("subject"),
            body=attrs.get("body", ""),
            variables=attrs.get("variables") or [],
            is_active=attrs.get("is_active", True),
        )
        try:
            entity.validate()
        except ValueError as e:
            raise serializers.ValidationError(str(e))

        return attrs
