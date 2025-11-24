"""Simple in-memory IP based rate limiter middleware."""
from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock
from typing import Deque, Dict, Iterable, Set

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class RateLimitStore:
    """Track individual IP usage and block windows."""

    def __init__(self) -> None:
        self._requests: Dict[str, Deque[float]] = defaultdict(deque)
        self._blocked_until: Dict[str, float] = {}
        self._lock = Lock()

    def is_blocked(self, ip: str, now: float | None = None) -> float:
        """Return seconds remaining of a block (0 when not blocked)."""
        current = now or time.time()
        with self._lock:
            blocked_until = self._blocked_until.get(ip)
            if not blocked_until:
                return 0.0
            if blocked_until <= current:
                self._blocked_until.pop(ip, None)
                return 0.0
            return blocked_until - current

    def note_request(
        self,
        ip: str,
        limit: int,
        window_seconds: int,
        block_seconds: int,
    ) -> tuple[bool, float, int]:
        """Register a hit and return (allowed, retry_after, remaining)."""
        now = time.time()
        with self._lock:
            blocked_until = self._blocked_until.get(ip)
            if blocked_until and blocked_until > now:
                return False, blocked_until - now, 0
            if blocked_until and blocked_until <= now:
                self._blocked_until.pop(ip, None)

            hits = self._requests[ip]
            cutoff = now - window_seconds
            while hits and hits[0] < cutoff:
                hits.popleft()

            hits.append(now)
            remaining = max(limit - len(hits), 0)
            if len(hits) > limit:
                self._blocked_until[ip] = now + block_seconds
                self._requests.pop(ip, None)
                return False, block_seconds, 0
            return True, 0.0, remaining


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """Starlette middleware that limits requests per client IP."""

    def __init__(
        self,
        app,
        store: RateLimitStore,
        limit: int,
        window_seconds: int,
        block_seconds: int,
        whitelist: Iterable[str] | None = None,
        enabled: bool = True,
    ) -> None:
        super().__init__(app)
        self.store = store
        self.limit = max(limit, 1)
        self.window_seconds = max(window_seconds, 1)
        self.block_seconds = max(block_seconds, 1)
        self.enabled = enabled
        self.whitelist: Set[str] = {
            ip.strip() for ip in (whitelist or []) if ip and ip.strip()
        }

    async def dispatch(self, request: Request, call_next) -> Response:
        if not self.enabled:
            return await call_next(request)

        client_ip = self._client_ip(request)
        if client_ip in self.whitelist:
            return await call_next(request)

        allowed, retry_after, remaining = self.store.note_request(
            client_ip,
            self.limit,
            self.window_seconds,
            self.block_seconds,
        )
        if allowed:
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Window"] = str(self.window_seconds)
            return response

        return JSONResponse(
            status_code=429,
            content={
                "detail": "Demasiadas peticiones desde esta IP. Intenta más tarde.",
                "retry_after_seconds": round(retry_after, 2),
            },
            headers={
                "Retry-After": str(int(retry_after) or self.block_seconds),
                "X-RateLimit-Limit": str(self.limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Window": str(self.window_seconds),
            },
        )

    @staticmethod
    def _client_ip(request: Request) -> str:
        client = request.client
        if client and client.host:
            return client.host
        # Fallback for proxied deployments that pass X-Forwarded-For but
        # where `client` is empty; we only inspect the first value.
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",", 1)[0].strip()
        return "unknown"
