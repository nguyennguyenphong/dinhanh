from rest_framework import serializers

from notifications.models.notification_templates import NotificationTemplate


class NotificationTemplateSerializer(serializers.ModelSerializer):
    tenant_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = NotificationTemplate
        fields = [
            "id",
            "tenant_id",
            "code",
            "name",
            "channel",
            "subject",
            "body",
            "variables",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        tenant_id = attrs.get("tenant_id")
        code = attrs.get("code")
        channel = attrs.get("channel")

        # Exclude current instance in unique check if updating
        exclude_id = self.instance.id if self.instance else None
        
        # We can call repositories or use django query directly for the validation:
        from notifications.providers.notification_provider import NotificationProvider
        
        if NotificationProvider.get_template()._template_repo().exists_by_code_channel(
            tenant_id=tenant_id,
            code=code,
            channel=channel,
            exclude_id=exclude_id
        ):
            raise serializers.ValidationError(
                {"code": f"Template with code '{code}' and channel '{channel}' already exists for this tenant."}
            )

        # Validate entity business logic
        from notifications.domain.entities.notification_template_entity import NotificationTemplateEntity
        entity = NotificationTemplateEntity(
            id=exclude_id,
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

    def create(self, validated_data):
        from notifications.providers.notification_provider import NotificationProvider
        from notifications.application.dtos.notification_templates.template_create_dto import NotificationTemplateCreateDTO
        
        dto = NotificationTemplateCreateDTO(
            tenant_id=validated_data["tenant_id"],
            code=validated_data["code"],
            name=validated_data["name"],
            channel=validated_data["channel"],
            body=validated_data["body"],
            subject=validated_data.get("subject"),
            variables=validated_data.get("variables") or [],
            is_active=validated_data.get("is_active", True),
        )
        
        response = NotificationProvider.create_template().execute(dto)
        return NotificationTemplate.objects.get(pk=response.id)

    def update(self, instance, validated_data):
        from notifications.providers.notification_provider import NotificationProvider
        from notifications.application.dtos.notification_templates.template_update_dto import NotificationTemplateUpdateDTO
        
        # Merge old values if not provided (for partial updates)
        dto = NotificationTemplateUpdateDTO(
            id=instance.id,
            tenant_id=validated_data.get("tenant_id", instance.tenant_id),
            code=validated_data.get("code", instance.code),
            name=validated_data.get("name", instance.name),
            channel=validated_data.get("channel", instance.channel),
            body=validated_data.get("body", instance.body),
            subject=validated_data.get("subject", instance.subject),
            variables=validated_data.get("variables", instance.variables) or [],
            is_active=validated_data.get("is_active", instance.is_active),
        )
        
        response = NotificationProvider.update_template().execute(dto)
        return NotificationTemplate.objects.get(pk=response.id)
