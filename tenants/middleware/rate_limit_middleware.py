import time

import redis
from django.conf import settings
from django.http import JsonResponse

redis_client = redis.Redis(host="127.0.0.1", port=6379, db=1, decode_responses=True)


class TenantRateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        self.RATE_LIMIT = 100
        self.WINDOW_SIZE = 60

    def __call__(self, request):
        if not request.path.startswith("/tenants/"):
            return self.get_response(request)

        if request.user and request.user.is_authenticated:
            identifier = f"user:{request.user.id}"
        else:
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                identifier = f"ip:{x_forwarded_for.split(',')[0].strip()}"
            else:
                identifier = f"ip:{request.META.get('REMOTE_ADDR')}"

        redis_key = f"ratelimit:{request.path}:{identifier}"

        current_time = time.time()
        clear_before_time = current_time - self.WINDOW_SIZE

        try:
            pipe = redis_client.pipeline()
            pipe.zremrangebyscore(redis_key, 0, clear_before_time)

            pipe.zcard(redis_key)
            pipe.zadd(redis_key, {str(current_time): current_time})

            # Set the auto-destruct time (TTL) for this key to clean up Redis RAM.
            pipe.expire(redis_key, self.WINDOW_SIZE + 5)

            # Run the entire command in Redis
            _, request_count, _, _ = pipe.execute()

            if request_count > self.RATE_LIMIT:
                # Returns standard RESTful API: HTTP 429 Too Many Requests
                response = JsonResponse(
                    {
                        "status": "error",
                        "code": "too_many_requests",
                        "message": "Bạn đang thao tác quá nhanh. Vui lòng thử lại sau ít phút.",
                    },
                    status=429,
                )
                # Provide an additional header to inform the frontend of the waiting time (in seconds).
                response["Retry-After"] = str(int(self.WINDOW_SIZE))
                return response

        except redis.RedisError:
            # Recommendation: If Redis suddenly crashes (loses connection), the system must still allow the request to proceed.
            # Don't let a rate limit system error cause the main business process to fail (Fail-open).
            pass

        return self.get_response(request)
