from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class UserEntity:
    """
    Domain representation of a UserAccount.
    Maintains user invariants and decoupling from database models.
    """

    id: int | None
    uuid: uuid.UUID
    tenant_id: int
    username: str
    email: str
    full_name: str
    phone: str | None
    avatar: str | None
    is_active: bool
    hashed_password: str
    branch_id: int | None = None
    must_change_password: bool = False
    password_expires_at: datetime | None = None
    locked_until: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    domain_events: list[Any] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        if not self.username or not self.username.strip():
            raise ValueError("Username cannot be empty.")
        if not self.email or not self.email.strip():
            raise ValueError("Email cannot be empty.")
        if self.tenant_id <= 0:
            raise ValueError("Invalid tenant_id. Must be a positive integer.")

    def deactivate(self) -> None:
        self.is_active = False

    def activate(self) -> None:
        self.is_active = True

    def update_info(
        self,
        full_name: str,
        phone: str | None,
        avatar: str | None,
        tenant_id: int | None = None,
        username: str | None = None,
        email: str | None = None,
        branch_id: int | None = None,
        must_change_password: bool = False,
        password_expires_at: datetime | None = None,
        locked_until: datetime | None = None,
    ) -> None:
        self.full_name = full_name.strip()
        self.phone = phone.strip() if phone else None
        self.avatar = avatar.strip() if avatar else None
        if tenant_id is not None:
            self.tenant_id = tenant_id
        if username is not None:
            self.username = username
        if email is not None:
            self.email = email
        self.branch_id = branch_id
        self.must_change_password = must_change_password
        self.password_expires_at = password_expires_at
        self.locked_until = locked_until

    def update_timestamp(self, now: datetime) -> None:
        self.updated_at = now
