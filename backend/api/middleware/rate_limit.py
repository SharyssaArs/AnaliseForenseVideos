from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.core.redis_client import redis_client


RATE_LIMIT = 10
WINDOW_SECONDS = 60
ANALYZE_PATH = "/analyze"


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method != "POST" or not request.url.path.endswith(ANALYZE_PATH):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}:analyze"

        current_count = redis_client.incr(key)

        if current_count == 1:
            redis_client.expire(key, WINDOW_SECONDS)

        if current_count > RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Limite de requisições excedido. Tente novamente em 60 segundos.",
                    }
                },
            )

        return await call_next(request)


def setup_rate_limit(app):
    app.add_middleware(RateLimitMiddleware)