"""
Auth — Bearer token extraction and TNC credit validation for PME products.
"""

from __future__ import annotations

import json
from contextvars import ContextVar
from typing import Optional

from starlette.types import ASGIApp, Receive, Scope, Send

from .database import get_tnc_balance, hash_key

_bearer_token: ContextVar[Optional[str]] = ContextVar("bearer_token", default=None)
_client_ip: ContextVar[Optional[str]] = ContextVar("client_ip", default=None)


def get_bearer_token() -> Optional[str]:
    return _bearer_token.get()


def get_client_ip() -> Optional[str]:
    return _client_ip.get()


def require_auth() -> str:
    """Assert authentication. Returns the token or raises ValueError."""
    token = _bearer_token.get()
    if not token:
        raise ValueError(
            "Authentication required. Include your ThinkNEO API key as Bearer token. "
            "Get your key at https://thinkneo.app/pricing"
        )
    return token


def require_tnc(tool_name: str, cost: float = 1.0) -> str:
    """Assert auth AND sufficient TNC balance."""
    token = require_auth()
    key_h = hash_key(token)
    balance = get_tnc_balance(key_h)
    if balance < cost:
        raise ValueError(
            f"Insufficient TNC credits. Tool '{tool_name}' costs {cost} TNC. "
            f"Your balance: {balance} TNC. Top up at https://thinkneo.app/pricing"
        )
    return token


class BearerTokenMiddleware:
    """ASGI middleware — extracts Bearer token and client IP into ContextVars."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] in ("http", "websocket"):
            headers = {k.lower(): v for k, v in scope.get("headers", [])}
            raw_auth = headers.get(b"authorization", b"").decode("utf-8", errors="ignore")
            token: Optional[str] = None
            if raw_auth.lower().startswith("bearer "):
                token = raw_auth[7:].strip() or None

            # Extract client IP
            ip = headers.get(b"x-forwarded-for", b"").decode().split(",")[0].strip()
            if not ip and scope.get("client"):
                ip = scope["client"][0]

            ctx_token = _bearer_token.set(token)
            ctx_ip = _client_ip.set(ip or None)
            try:
                await self.app(scope, receive, send)
            finally:
                _bearer_token.reset(ctx_token)
                _client_ip.reset(ctx_ip)
        else:
            await self.app(scope, receive, send)
