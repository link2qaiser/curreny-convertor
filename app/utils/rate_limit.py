import asyncio
import ipaddress
import logging
import time
from collections import OrderedDict, deque

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import env_var

logger = logging.getLogger(__name__)


def _parse_trusted_proxies(raw: str) -> list[ipaddress._BaseNetwork]:
    nets: list[ipaddress._BaseNetwork] = []
    for chunk in (raw or "").split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            nets.append(ipaddress.ip_network(chunk, strict=False))
        except ValueError:
            logger.warning(f"Ignoring invalid TRUSTED_PROXIES entry: {chunk!r}")
    return nets


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Per-IP sliding-window rate limiter.

    Soft limit: once exceeded, the response is delayed by SOFT_DELAY_MS.
    Hard limit: once exceeded, the request is rejected with HTTP 429.

    X-Forwarded-For is only honored when the immediate socket peer is in
    TRUSTED_PROXIES; otherwise the peer address is used. This prevents
    spoofed headers from bypassing limits or inflating the in-memory map.
    Total tracked IPs are capped at MAX_TRACKED_IPS (oldest evicted).
    """

    def __init__(self, app):
        super().__init__(app)
        self._hits: OrderedDict[str, deque[float]] = OrderedDict()
        self._lock = asyncio.Lock()
        self._trusted_proxies = _parse_trusted_proxies(env_var.TRUSTED_PROXIES)

    def _peer_is_trusted(self, peer: str | None) -> bool:
        if not peer or not self._trusted_proxies:
            return False
        try:
            addr = ipaddress.ip_address(peer)
        except ValueError:
            return False
        return any(addr in net for net in self._trusted_proxies)

    def _client_ip(self, request: Request) -> str:
        peer = request.client.host if request.client else None
        if self._peer_is_trusted(peer):
            fwd = request.headers.get("x-forwarded-for")
            if fwd:
                # XFF is left-to-right: original client first.
                return fwd.split(",")[0].strip()
        return peer or "unknown"

    async def dispatch(self, request: Request, call_next):
        window = env_var.RATE_LIMIT_WINDOW_SECONDS
        soft = env_var.RATE_LIMIT_SOFT
        hard = env_var.RATE_LIMIT_HARD
        soft_delay = env_var.RATE_LIMIT_SOFT_DELAY_MS / 1000.0
        max_tracked = env_var.RATE_LIMIT_MAX_TRACKED_IPS

        ip = self._client_ip(request)
        now = time.monotonic()
        cutoff = now - window

        async with self._lock:
            bucket = self._hits.get(ip)
            if bucket is None:
                bucket = deque()
                self._hits[ip] = bucket
            else:
                self._hits.move_to_end(ip)
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            count = len(bucket) + 1
            bucket.append(now)
            while len(self._hits) > max_tracked:
                self._hits.popitem(last=False)

        if count > hard:
            logger.warning(f"Rate limit HARD hit ip={ip} count={count} limit={hard}")
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded",
                    "limit": hard,
                    "window_seconds": window,
                },
                headers={
                    "Retry-After": str(window),
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
