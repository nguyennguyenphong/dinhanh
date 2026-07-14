"""
Domain entity representing a Notification log / outbound queue message.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class NotificationEntity:
    id: int | None
    tenant_id: int
    template_id: int | None
    recipient_type: str
    recipient_id: int | None
    recipient_phone: str | None
    recipient_email: str | None
    channel: str
    subject: str | None
    body: str
    status: str = "PENDING"
    retry_count: int = 0
    error_msg: str | None = None
    ref_type: str | None = None
    ref_id: int | None = None
    sent_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def validate(self) -> None:
        """
        Validates routing rules before sending.
        """
        if self.recipient_type not in ["USER", "CUSTOMER", "EMPLOYEE"]:
            raise ValueError(
                f"Invalid recipient type: {self.recipient_type}. Expected USER, CUSTOMER, or EMPLOYEE."
            )

        if self.channel == "EMAIL" and not self.recipient_email:
            raise ValueError(
                "Routing Error: EMAIL channel requires a recipient email address."
            )

        if self.channel in ["SMS", "ZALO"] and not self.recipient_phone:
            raise ValueError(
                "Routing Error: SMS/ZALO channels require a recipient phone number."
            )

    def mark_as_transmitted(self, now: datetime) -> None:
        self.status = "SENT"
        self.sent_at = now
        self.error_msg = None

    def mark_as_failed(self, error_msg: str) -> None:
        self.error_msg = error_msg
        if self.retry_count < 3:
            self.status = "PENDING"
            self.retry_count += 1
        else:
            self.status = "FAILED"
