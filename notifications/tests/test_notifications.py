from unittest.mock import MagicMock

import pytest

from notifications.application.dtos.notification_templates.notification_template_create_dto import (
    NotificationTemplateCreateDTO,
)
from notifications.application.usecases.notification_templates.notification_template_create_usecase import (
    NotificationTemplateCreateUseCase,
)
from notifications.domain.entities.notification_entity import NotificationEntity
from notifications.domain.entities.notification_template_entity import (
    NotificationTemplateEntity,
)
from notifications.exceptions.exceptions import NotificationTemplateAlreadyExistsError


class TestNotificationTemplateEntity:
    def test_entity_validates_email_requires_subject(self):
        entity = NotificationTemplateEntity(
            id=None,
            tenant_id=1,
            code="TEST",
            name="Test",
            channel="EMAIL",
            subject=None,
            body="Hello {name}",
            variables=["name"],
        )
        with pytest.raises(
            ValueError,
            match="Compliance Error: EMAIL channel blueprints require a subject line.",
        ):
            entity.validate()

    def test_entity_validates_variables_match_body(self):
        entity = NotificationTemplateEntity(
            id=None,
            tenant_id=1,
            code="TEST",
            name="Test",
            channel="SMS",
            subject=None,
            body="Hello {name} {age}",
            variables=["name"],
        )
        with pytest.raises(
            ValueError,
            match="Variable '\{age\}' detected in body but not listed in variables",
        ):
            entity.validate()

    def test_entity_renders_successfully(self):
        entity = NotificationTemplateEntity(
            id=1,
            tenant_id=1,
            code="TEST",
            name="Test",
            channel="EMAIL",
            subject="Alert {name}",
            body="Hello {name}, your code is {code}",
            variables=["name", "code"],
        )
        subject, body = entity.render({"name": "Phong", "code": "1234"})
        assert subject == "Alert Phong"
        assert body == "Hello Phong, your code is 1234"


class TestCreateTemplateUseCase:
    def test_raises_when_template_already_exists(self):
        repo = MagicMock()
        repo.exists_by_code_channel.return_value = True

        usecase = NotificationTemplateCreateUseCase(repo)
        dto = NotificationTemplateCreateDTO(
            tenant_id=1,
            code="OTP",
            name="OTP Message",
            channel="SMS",
            body="Your OTP is {otp}",
            variables=["otp"],
        )

        with pytest.raises(NotificationTemplateAlreadyExistsError):
            usecase.execute(dto)


@pytest.mark.django_db
class TestNotificationIntegration:
    def test_create_and_fetch_template_orm(self):
        from notifications.models.notification_templates import NotificationTemplate
        from notifications.repositories.implement.notification_template_repository_impl import (
            NotificationTemplateRepositoryImpl,
        )

        # Test DB unique constraints and repository creation
        repo = NotificationTemplateRepositoryImpl()

        entity = NotificationTemplateEntity(
            id=None,
            tenant_id=1,
            code="CONFIRM",
            name="Confirmation Email",
            channel="EMAIL",
            subject="Welcome {name}!",
            body="Welcome {name} to our service.",
            variables=["name"],
        )

        saved = repo.create(entity)
        assert saved.id is not None

        fetched = repo.get_by_id(saved.id)
        assert fetched is not None
        assert fetched.code == "CONFIRM"
        assert fetched.subject == "Welcome {name}!"

        # Verify lists
        items, count = repo.list(filters={"tenant_id": 1, "channel": "EMAIL"})
        assert count == 1
        assert items[0].code == "CONFIRM"
