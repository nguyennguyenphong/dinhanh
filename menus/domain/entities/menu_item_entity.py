from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional

from menus.constants import MenuItemDefaults


@dataclass
class MenuItemEntity:
    """
    Domain representation of a MenuItem.
    Handles nested hierarchy invariants and URL routing configuration capabilities.
    """

    id: Optional[int]
    uuid: uuid.UUID
    tenant_id: int
    code: str
    label: str
    group_id: Optional[int] = None
    parent_id: Optional[int] = None
    url_name: Optional[str] = None
    url_path: Optional[str] = None
    icon: Optional[str] = None
    badge: Optional[MenuItemDefaults] = None
    permission_code: Optional[str] = None
    sort_order: int = MenuItemDefaults.SORT_ORDER
    open_in_new_tab: bool = False
    is_active: bool = MenuItemDefaults.IS_ACTIVE
    is_hidden: bool = MenuItemDefaults.IS_HIDDEN
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Track domain events (e.g., MenuItemMoved, MenuItemVisibilityChanged)
    domain_events: List[Any] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Validates aggregate and domain invariants.
        """
        # 1. Base Validations
        if self.tenant_id <= 0:
            raise ValueError("tenant_id must be a positive integer.")

        if self.group_id is not None and self.group_id <= 0:
            raise ValueError("group_id must be a positive integer if provided.")

        if not self.label or not self.label.strip():
            raise ValueError("MenuItem label cannot be empty.")

        # 2. Code format validation (matches database RegexValidator)
        if not re.match(r"^[a-z0-9_]+$", self.code):
            raise ValueError(
                "Code must contain only lowercase letters, numbers, and underscores."
            )

        # 3. Hierarchy Guard
        if self.parent_id is not None and self.parent_id <= 0:
            raise ValueError("parent_id must be a positive integer if provided.")

        if self.id is not None and self.parent_id == self.id:
            raise ValueError("Menu item cannot be its own parent.")

        # 4. URL Strategy Guard
        if not self.url_name and not self.url_path:
            raise ValueError("Either url_name or url_path must be provided.")

        # Self-sanitization
        self.code = self.code.strip()
        self.label = self.label.strip()
        if self.url_name:
            self.url_name = self.url_name.strip()
        if self.url_path:
            self.url_path = self.url_path.strip()

    # ------------------------------------------------------------------
    # Business Rules & Behaviors (Write / Mutations)
    # ------------------------------------------------------------------

    def update_routing(self, url_name: Optional[str], url_path: Optional[str]) -> None:
        """
        Safely updates routing mechanism verifying the domain rules.
        """
        if not url_name and not url_path:
            raise ValueError(
                "Cannot clear routing. Either url_name or url_path must remain."
            )
        self.url_name = url_name
        self.url_path = url_path

    def move_to_parent(self, parent_entity: Optional[MenuItemEntity]) -> None:
        """
        Changes parent relation and strictly checks for multi-tenant boundary alignment
        and potential circular reference up to 1 level here.
        (Deep circular hierarchy check should be executed via a Domain Service).
        """
        if parent_entity is None:
            self.parent_id = None
            return

        if parent_entity.tenant_id != self.tenant_id:
            raise ValueError("Parent menu item must belong to the same tenant.")

        if parent_entity.id == self.id and self.id is not None:
            raise ValueError("Menu item cannot be its own parent.")

        self.parent_id = parent_entity.id

    def set_badge(self, text: Optional[str]) -> None:
        """
        Updates or removes the badge properties using Value Object stability.
        """
        if not text or not text.strip():
            self.badge = None
        else:
            self.badge = MenuItemDefaults.BADGE_COLOR

    def change_visibility(self, is_active: bool, is_hidden: bool) -> None:
        """
        Updates node rendering state flags.
        """
        self.is_active = is_active
        self.is_hidden = is_hidden

    # ------------------------------------------------------------------
    # Business Queries (Read / Evaluations)
    # ------------------------------------------------------------------

    def is_visible_to_user(
        self, user_is_superuser: bool, user_permissions: List[str]
    ) -> bool:
        """
        Determines pure permission availability.
        Decoupled from Django's `user.has_permission` mechanics.
        """
        if not self.is_active or self.is_hidden:
            return False

        if user_is_superuser:
            return True

        if not self.permission_code:
            return True

        return self.permission_code in user_permissions

    def resolve_url_strategy(
        self, reversed_django_url: Optional[str] = None
    ) -> Optional[str]:
        """
        Execution of the specification logic. Since Domain can't access Django's `reverse()`,
        the resolved reverse URL is optionally passed from infrastructure layer.
        """
        if reversed_django_url:
            return reversed_django_url
        return self.url_path if self.url_path else None
