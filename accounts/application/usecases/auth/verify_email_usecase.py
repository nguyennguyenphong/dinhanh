from __future__ import annotations

from accounts.application.dtos.auth.auth_dto import VerifyEmailDto
from accounts.domain.entities.user_entity import UserEntity
from accounts.repositories.interfaces.otp_code_repository_interface import (
    OTPCodeRepository,
)
from accounts.repositories.interfaces.user_repository_interface import UserRepository


class VerifyEmailUseCase:

    def __init__(self, user_repo: UserRepository, otp_repo: OTPCodeRepository):
        self._user_repo = user_repo
        self._otp_repo = otp_repo

    def execute(self, dto: VerifyEmailDto) -> UserEntity:
        otp_entity = self._otp_repo.get_valid_otp(
            email=dto.email.strip().lower(),
            code=dto.code.strip(),
            purpose="REGISTER",
        )

        if not otp_entity:
            raise ValueError("Mã xác thực không hợp lệ hoặc đã hết hạn.")

        user_entity = self._user_repo.find_by_email(dto.email.strip().lower())
        if not user_entity:
            raise ValueError("Không tìm thấy thông tin tài khoản.")

        user_entity.activate()
        saved_user = self._user_repo.save(user_entity)

        # Mark OTP as used
        otp_entity.mark_used()
        self._otp_repo.save(otp_entity)

        return saved_user
