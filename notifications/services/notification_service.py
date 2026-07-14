from __future__ import annotations

import logging
from typing import Any

from django.utils import timezone

from notifications.application.dtos.notifications.notification_create_dto import (
    NotificationCreateDTO,
)
from notifications.providers.notification_provider import NotificationProvider

logger = logging.getLogger(__name__)


class NotificationService:

    @classmethod
    def render_and_send(
        cls,
        *,
        tenant_id: int,
        template_code: str,
        channel: str,
        recipient_type: str,
        context: dict[str, Any],
        recipient_id: int | None = None,
        recipient_phone: str | None = None,
        recipient_email: str | None = None,
        ref_type: str | None = None,
        ref_id: int | None = None,
    ) -> int:
        """
        Retrieves a template, renders it, and stages a Notification log entry.
        Returns the staged notification ID.
        """
        # Fetch template
        template = NotificationProvider.get_template().by_code(
            tenant_id=tenant_id, code=template_code, channel=channel
        )

        # Render template
        subject, body = NotificationProvider.get_template()._template_repo().get_by_id(
            template.id
        ).render(context)  # type: ignore

        # Stage Notification DTO
        dto = NotificationCreateDTO(
            tenant_id=tenant_id,
            template_id=template.id,
            recipient_type=recipient_type,
            recipient_id=recipient_id,
            recipient_phone=recipient_phone,
            recipient_email=recipient_email,
            channel=channel,
            subject=subject,
            body=body,
            ref_type=ref_type,
            ref_id=ref_id,
        )

        response = NotificationProvider.create_notification().execute(dto)
        return response.id

    @classmethod
    def dispatch_now(cls, notification_id: int) -> bool:
        """
        Immediately sends the message via its respective channel gateway.
        """
        notification = NotificationProvider.get_notification().execute(notification_id)
        if notification.status not in ["PENDING"]:
            return False

        channel = notification.channel.upper()
        success = False
        error_msg = None

        try:
            if channel == "EMAIL":
                success, error_msg = cls._send_email(
                    recipient=notification.recipient_email,
                    subject=notification.subject,
                    body=notification.body,
                )
            elif channel == "SMS":
                success, error_msg = cls._send_sms(
                    recipient=notification.recipient_phone,
                    body=notification.body,
                )
            elif channel == "ZALO":
                success, error_msg = cls._send_zalo(
                    recipient=notification.recipient_phone,
                    body=notification.body,
                )
            elif channel == "PUSH":
                success, error_msg = cls._send_push(
                    recipient_id=notification.recipient_id,
                    recipient_type=notification.recipient_type,
                    subject=notification.subject,
                    body=notification.body,
                )
            elif channel == "IN_APP":
                success, error_msg = cls._send_in_app(
                    recipient_id=notification.recipient_id,
                    recipient_type=notification.recipient_type,
                    subject=notification.subject,
                    body=notification.body,
                )
            else:
                raise ValueError(f"Unsupported channel: {channel}")

        except Exception as e:
            logger.exception("Error during dispatching notification #%d", notification_id)
            success = False
            error_msg = str(e)

        if success:
            NotificationProvider.update_notification_status().mark_sent(
                notification_id, sent_at=timezone.now()
            )
            return True
        else:
            NotificationProvider.update_notification_status().mark_failed(
                notification_id, error_msg or "Unknown error occurred"
            )
            return False

    @staticmethod
    def _send_email(recipient: str | None, subject: str | None, body: str) -> tuple[bool, str | None]:
        if not recipient:
            return False, "Missing recipient email"
        # Integration placeholder (e.g. django.core.mail or SendGrid API wrapper)
        logger.info("Sending Email to %s: %s | %s", recipient, subject, body)
        return True, None

    @staticmethod
    def _send_sms(recipient: str | None, body: str) -> tuple[bool, str | None]:
        if not recipient:
            return False, "Missing recipient phone"
        # Integration placeholder (e.g. Twilio, eSMS API wrapper)
        logger.info("Sending SMS to %s: %s", recipient, body)
        return True, None

    @staticmethod
    def _send_zalo(recipient: str | None, body: str) -> tuple[bool, str | None]:
        if not recipient:
            return False, "Missing recipient phone"
        # Integration placeholder (e.g. ZNS API wrapper)
        logger.info("Sending ZALO ZNS to %s: %s", recipient, body)
        return True, None

    @staticmethod
    def _send_push(
        recipient_id: int | None, recipient_type: str, subject: str | None, body: str
    ) -> tuple[bool, str | None]:
        # Integration placeholder (e.g. Firebase Cloud Messaging / Expo)
        logger.info("Sending FCM Push notification to %s #%s: %s | %s", recipient_type, recipient_id, subject, body)
        return True, None

    @staticmethod
    def _send_in_app(
        recipient_id: int | None, recipient_type: str, subject: str | None, body: str
    ) -> tuple[bool, str | None]:
        # Logged internally in dashboard/bell systems
        logger.info("Sending In-app notification to %s #%s: %s | %s", recipient_type, recipient_id, subject, body)
        return True, None
