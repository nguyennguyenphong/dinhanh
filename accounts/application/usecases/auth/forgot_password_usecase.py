from __future__ import annotations

import random
from datetime import timedelta

from django.core.mail import send_mail
from django.utils import timezone

from accounts.application.dtos.auth.auth_dto import ForgotPasswordDto
from accounts.domain.entities.otp_code_entity import OTPCodeEntity
from accounts.repositories.interfaces.otp_code_repository_interface import (
    OTPCodeRepository,
)
from accounts.repositories.interfaces.user_repository_interface import UserRepository


class ForgotPasswordUseCase:

    def __init__(self, user_repo: UserRepository, otp_repo: OTPCodeRepository):
        self._user_repo = user_repo
        self._otp_repo = otp_repo

    def execute(self, dto: ForgotPasswordDto, tenant_id: int = 1) -> None:
        user_entity = self._user_repo.find_by_email(dto.email.strip().lower())
        if not user_entity:
            raise ValueError("Email này chưa được đăng ký trong hệ thống.")

        # Generate 6-digit OTP
        code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timedelta(minutes=10)

        otp_entity = OTPCodeEntity(
            id=None,
            email=dto.email.strip().lower(),
            code=code,
            purpose="PASSWORD_RESET",
            expires_at=expires_at,
            is_used=False,
        )

        self._otp_repo.save(otp_entity)

        # Send email
        from django.template.loader import render_to_string
        subject = "Khôi phục mật khẩu tài khoản"
        html_message = render_to_string("email/inform/password_reset_otp.html", {"code": code})
        from_email = "no-reply@dinhanh.com"
        recipient_list = [dto.email.strip().lower()]

        try:
            send_mail(
                subject, html_message, from_email, recipient_list, fail_silently=True
            )
        except Exception:
            pass
