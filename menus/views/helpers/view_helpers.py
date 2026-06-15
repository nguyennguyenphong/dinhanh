"""
Shared view helpers: pagination envelope, context extraction, error mapping.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from menus.exceptions import (
    MenuGroupAlreadyExistsError,
    MenuGroupDomainError,
    MenuGroupNotFoundError,
)


@dataclass
class RequestContext:
    """Extracts commonly needed values from the DRF request."""

    actor_id: int | None
    actor_username: str | None
    ip_address: str | None
    user_agent: str | None

    @classmethod
    def from_request(cls, request: Request) -> "RequestContext":
        user = getattr(request, "user", None)
        return cls(
            actor_id=user.pk if user and user.is_authenticated else None,
            actor_username=user.username if user and user.is_authenticated else None,
            ip_address=cls._get_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT"),
        )

    @staticmethod
    def _get_ip(request: Request) -> str | None:
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


def paginated_response(
    data: list[Any],
    total: int,
    limit: int,
    offset: int,
    serializer_class: Any = None,
) -> Response:
    """
    Standard paginated envelope:
    {
        "count": <total>,
        "limit": <limit>,
        "offset": <offset>,
        "results": [...]
    }
    """
    if serializer_class:
        results = serializer_class(data, many=True).data
    else:
        results = data

    return Response(
        {
            "count": total,
            "limit": limit,
            "offset": offset,
            "results": results,
        }
    )


def domain_error_response(exc: MenuGroupDomainError) -> Response:
    """
    Maps domain exceptions to appropriate HTTP responses.
    Call this in views' except blocks.
    """
    mapping: dict[type, tuple[int, str]] = {
        MenuGroupNotFoundError: (status.HTTP_404_NOT_FOUND, "Not found."),
        MenuGroupAlreadyExistsError: (status.HTTP_409_CONFLICT, "Already exists."),
    }
    http_status, default_msg = mapping.get(
        type(exc), (status.HTTP_400_BAD_REQUEST, str(exc))
    )
    return Response({"detail": str(exc) or default_msg}, status=http_status)
