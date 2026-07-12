import threading

from django.utils.deprecation import MiddlewareMixin

# The variable stores the user information for each individual request (thread-safe).
_thread_local = threading.local()


def get_current_user():
    """The function retrieves the user from anywhere in the code."""
    return getattr(_thread_local, "user", None)


class CurrentUserMiddleware(MiddlewareMixin):
    def process_request(self, request):
        _thread_local.user = request.user if request.user.is_authenticated else None


class UserSecurityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            return None

        from django.contrib import messages
        from django.shortcuts import redirect
        from django.urls import Resolver404, resolve
        from django.utils import timezone

        # Check if user is locked
        if hasattr(request.user, "is_locked") and request.user.is_locked():
            from django.contrib.auth import logout

            logout(request)
            messages.error(request, "Tài khoản của bạn đã bị khóa.")
            return redirect("login")

        # Resolve request path name to avoid redirect loop
        try:
            resolver_match = resolve(request.path_info)
            url_name = resolver_match.url_name
        except Resolver404:
            url_name = None

        # Exempt URLs from must_change_password / password_expired redirection
        exempt_url_names = ["password_change", "logout"]
        if (
            url_name in exempt_url_names
            or request.path_info.startswith("/static/")
            or request.path_info.startswith("/media/")
        ):
            return None

        must_change = getattr(request.user, "must_change_password", False)

        # Check if password has expired
        password_expired = False
        password_expires_at = getattr(request.user, "password_expires_at", None)
        if password_expires_at and timezone.now() > password_expires_at:
            password_expired = True

        if must_change or password_expired:
            if password_expired:
                messages.warning(
                    request, "Mật khẩu của bạn đã hết hạn. Vui lòng đổi mật khẩu mới."
                )
            else:
                messages.warning(
                    request,
                    "Bạn được yêu cầu đổi mật khẩu để tiếp tục sử dụng hệ thống.",
                )
            return redirect("password_change")

        return None
