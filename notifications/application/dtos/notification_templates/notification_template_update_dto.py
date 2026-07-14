from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class NotificationTemplateUpdateDTO:
    id: int
    tenant_id: int
    code: str
    name: str
    channel: str
    body: str
    subject: str | None = None
    variables: list[str] = field(default_factory=list)
    is_active: bool = True
