"""
Domain entities for Notification Bounded Context.
Pure Python dataclasses — no Django ORM dependency.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class NotificationTemplateEntity:
    """
    Domain representation of a Notification Template blueprint.
    """

    id: int | None
    tenant_id: int
    code: str
    name: str
    channel: str
    subject: str | None
    body: str
    variables: list[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def validate(self) -> None:
        """
        Validate business rules for templates.
        """
        if self.channel == "EMAIL" and not self.subject:
            raise ValueError(
                "Compliance Error: EMAIL channel blueprints require a subject line."
            )

        if self.body and self.variables:
            extracted = re.findall(r"\{([^}]+)\}", self.body)
            for var in extracted:
                if var not in self.variables:
                    raise ValueError(
                        f"Compilation Discrepancy: Variable '{{{var}}}' detected in body but not listed in variables."
                    )

    def render(self, context: dict[str, Any]) -> tuple[str, str]:
        """
        Hydrate templates dynamic curly brackets placeholders.
        """
        if not self.is_active:
            raise ValueError("Execution Block: Target template is disabled.")

        try:
            rendered_body = self.body.format(**context)
            rendered_subject = ""
            if self.subject:
                rendered_subject = self.subject.format(**context)
            return rendered_subject, rendered_body
        except KeyError as err:
            raise KeyError(
                f"Hydration Error: Required context key '{{{err.args[0]}}}' missing from data argument injection."
            )
