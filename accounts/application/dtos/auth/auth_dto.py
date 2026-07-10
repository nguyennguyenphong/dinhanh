from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterDto:
    username: str
    email: str
    password: str
    full_name: str
    phone: str | None = None


@dataclass(frozen=True)
class VerifyEmailDto:
    email: str
    code: str


@dataclass(frozen=True)
class ForgotPasswordDto:
    email: str


@dataclass(frozen=True)
class ConfirmPasswordResetDto:
    email: str
    code: str
    new_password: str
