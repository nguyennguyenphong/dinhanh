from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class MenuItemRoleEntity:
    """
    Domain Representation of the association between a MenuItem and a Role.
    Encapsulates multi-tenant consistency and cache invalidation side-effects indicators.
    """

    id: Optional[int]
    uuid: Optional[str]
    menu_item_id: int
    role_id: int
    tenant_id: int

    # Advanced DDD: Track changes to clear internal or distributed caching mechanisms
    domain_events: List[Any] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Validates aggregate data boundaries right after instantiation.
        """
        if self.menu_item_id <= 0:
            raise ValueError("menu_item_id must be a positive integer.")
        if self.role_id <= 0:
            raise ValueError("role_id must be a positive integer.")
        if self.tenant_id <= 0:
            raise ValueError("tenant_id must be a positive integer.")

    # ------------------------------------------------------------------
    # Factory Methods (Named Constructors)
    # ------------------------------------------------------------------

    @classmethod
    def create_assignment(
        cls, menu_item_id: int, role_id: int, tenant_id: int
    ) -> MenuItemRoleEntity:
        """
        Factory to handle clean intent creation from application use cases.
        """
        assignment = cls(
            id=None,
            uuid=None,
            menu_item_id=menu_item_id,
            role_id=role_id,
            tenant_id=tenant_id,
        )
        # Register a side-effect intent event for cache clear operations
        assignment._record_cache_invalidation_event()
        return assignment

    # ------------------------------------------------------------------
    # Domain Side-Effects Management
    # ------------------------------------------------------------------

    def mark_for_revocation(self) -> None:
        """
        Prepares entity to be destroyed, staging cache clearance commands.
        """
        self._record_cache_invalidation_event()

    def _record_cache_invalidation_event(self) -> None:
        """
        Produces structural domain event indications. Tightly decoupled from
        Django's `django.core.cache`. The application service or repository will
        listen to this and safely clear Redis/Memcached entries.
        """
        # Example tracking keys dictionary
        self.domain_events.append(
            {
                "event_type": "MENU_ITEM_ROLE_CACHE_INVALIDATE",
                "keys": [
                    f"menu_item_{self.menu_item_id}_roles",
                    f"role_{self.role_id}_menu_items",
                ],
            }
        )
