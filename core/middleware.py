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