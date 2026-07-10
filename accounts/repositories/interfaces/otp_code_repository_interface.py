from __future__ import annotations

from typing import Protocol

from accounts.domain.entities.otp_code_entity import OTPCodeEntity


class OTPCodeRepository(Protocol):
    """
    Contract for OTP code persistence operations.
    """

    def save(self, entity: OTPCodeEntity) -> OTPCodeEntity:
        """Persist or update OTPCodeEntity."""
        ...

    def get_valid_otp(
        self, email: str, code: str, purpose: str
    ) -> OTPCodeEntity | None:
        """Retrieve a non-expired, unused OTPCodeEntity."""
        ...
