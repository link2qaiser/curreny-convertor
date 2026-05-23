import asyncio
import logging
import time
from collections import defaultdict, deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import env_var

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP sliding-window rate limiter.

    Soft limit: once exceeded, the response is delayed by SOFT_DELAY_MS.
    Hard limit: once exceeded, the request is rejected with HTTP 429.
    Counters live in-process memory and reset on restart.
    """

    def __init__(self, app):
        super().__init__(app)
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    def _client_ip(self, request: Request) -> str:
        fwd = request.headers.get("x-forwarded-for")
        if fwd:
            return fwd.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next):
        window = env_var.RATE_LIMIT_WINDOW_SECONDS
        soft = env_var.RATE_LIMIT_SOFT
        hard = env_var.RATE_LIMIT_HARD
        soft_delay = env_var.RATE_LIMIT_SOFT_DELAY_MS / 1000.0

        ip = self._client_ip(request)
        now = time.monotonic()
        cutoff = now - window

        async with self._lock:
            bucket = self._hits[ip]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            count = len(bucket) + 1
            bucket.append(now)

        if count > hard:
            retry_after = window
            logger.warning(f"Rate limit HARD hit ip={ip} count={count} limit={hard}")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "limit": hard,
                    "window_seconds": window,
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(hard),
                    "X-RateLimit-Remaining": "0",
                },
            )

        throttled = count > soft
        if throttled:
            logger.info(f"Rate limit SOFT hit ip={ip} count={count} limit={soft} — throttling")
            await asyncio.sleep(soft_delay)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit-Soft"] = str(soft)
        response.headers["X-RateLimit-Limit-Hard"] = str(hard)
        response.headers["X-RateLimit-Remaining-Hard"] = str(max(hard - count, 0))
        if throttled:
            response.headers["X-RateLimit-Throttled"] = "true"
        return response
