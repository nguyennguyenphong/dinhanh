from __future__ import annotations

from typing import Any

from django.utils import timezone

from accounts.domain.entities.otp_code_entity import OTPCodeEntity
from accounts.repositories.interfaces.otp_code_repository_interface import (
    OTPCodeRepository,
)


def _model_to_entity(obj: Any) -> OTPCodeEntity:
    return OTPCodeEntity(
        id=obj.pk,
        email=obj.email,
        code=obj.code,
        purpose=obj.purpose,
        expires_at=obj.expires_at,
        is_used=obj.is_used,
        created_at=obj.created_at,
        updated_at=obj.updated_at,
    )


class OTPCodeRepositoryImpl(OTPCodeRepository):

    @property
    def _model(self):
        from accounts.models.otp_code import OTPCode

        return OTPCode

    def save(self, entity: OTPCodeEntity) -> OTPCodeEntity:
        if entity.id:
            obj = self._model.objects.filter(pk=entity.id).first()
            if not obj:
                raise ValueError("OTP Code not found to update")
            obj.is_used = entity.is_used
            obj.save()
        else:
            obj = self._model(
                email=entity.email.strip().lower(),
                code=entity.code,
                purpose=entity.purpose,
                expires_at=entity.expires_at,
                is_used=entity.is_used,
            )
            obj.save()

        return _model_to_entity(obj)

    def get_valid_otp(
        self, email: str, code: str, purpose: str
    ) -> OTPCodeEntity | None:
        now = timezone.now()
        obj = (
            self._model.objects.filter(
                email=email.strip().lower(),
                code=code.strip(),
                purpose=purpose,
                is_used=False,
                expires_at__gt=now,
            )
            .order_by("-created_at")
            .first()
        )
        return _model_to_entity(obj) if obj else None
