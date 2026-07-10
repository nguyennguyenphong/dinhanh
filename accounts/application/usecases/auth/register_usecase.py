from __future__ import annotations

import random
import uuid
from datetime import timedelta

from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.utils import timezone

from accounts.application.dtos.auth.auth_dto import RegisterDto
from accounts.domain.entities.otp_code_entity import OTPCodeEntity
from accounts.domain.entities.user_entity import UserEntity
from accounts.repositories.interfaces.otp_code_repository_interface import (
    OTPCodeRepository,
)
from accounts.repositories.interfaces.user_repository_interface import UserRepository


class RegisterUseCase:

    def __init__(
        self, user_repo: UserRepository, otp_repo: OTPCodeRepository
    ):
        self._user_repo = user_repo
        self._otp_repo = otp_repo

    def execute(self, dto: RegisterDto, tenant_id: int = 1) -> UserEntity:
        if self._user_repo.exists_by_username(tenant_id=tenant_id, username=dto.username):
            raise ValueError("Tên đăng nhập đã tồn tại.")

        if self._user_repo.exists_by_email(tenant_id=tenant_id, email=dto.email):
            raise ValueError("Email đã tồn tại.")

        # Create user as inactive
        user_entity = UserEntity(
            id=None,
            uuid=uuid.uuid4(),
            tenant_id=tenant_id,
            username=dto.username.strip().lower(),
            email=dto.email.strip().lower(),
            full_name=dto.full_name,
            phone=dto.phone,
            avatar=None,
            is_active=False,
            hashed_password=make_password(dto.password),
        )

        saved_user = self._user_repo.save(user_entity)

        # Generate 6-digit OTP
        code = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timedelta(minutes=10)

        otp_entity = OTPCodeEntity(
            id=None,
            email=dto.email.strip().lower(),
            code=code,
            purpose="REGISTER",
            expires_at=expires_at,
            is_used=False,
        )

        self._otp_repo.save(otp_entity)

        # Send email
        subject = "Xác nhận đăng ký tài khoản"
        message = f"Mã xác thực đăng ký tài khoản của bạn là: {code}. Mã này có hiệu lực trong 10 phút."
        from_email = "no-reply@dinhanh.com"
        recipient_list = [dto.email.strip().lower()]

        try:
            send_mail(
                subject, message, from_email, recipient_list, fail_silently=True
            )
        except Exception:
            # Silence email errors for robust offline testing/running
            pass

        return saved_user
