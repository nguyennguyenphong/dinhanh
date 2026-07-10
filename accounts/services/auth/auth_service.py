from django.contrib.auth import authenticate

from accounts.application.dtos import LoginDTO


class LoginService:
    """
    Wrapper around Django core security backend features.
    Handles algorithmic password checking to prevent timing/side-channel attacks.
    """

    def verify_credentials(self, dto: LoginDTO, request=None) -> bool:
        """
        Invokes native framework logic to test password validity against database hash.
        """
        return authenticate(request, username=dto.email, password=dto.password)
