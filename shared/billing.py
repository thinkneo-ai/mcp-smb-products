"""
TNC Billing — wraps tool functions with credit deduction.
"""

from __future__ import annotations

import functools
import json
import logging
from typing import Any, Callable

from .auth import get_bearer_token, get_client_ip
from .database import deduct_tnc, get_monthly_usage, get_tnc_balance, hash_key

logger = logging.getLogger(__name__)

# Default TNC cost per tool call (can be overridden per tool)
DEFAULT_TNC_COST = 1.0


def tnc_tool(product: str, cost: float = DEFAULT_TNC_COST):
    """
    Decorator for MCP tool functions that charges TNC credits.
    Wraps the tool to:
    1. Validate auth + balance
    2. Deduct TNC
    3. Append usage footer
    """

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            token = get_bearer_token()
            if not token:
                return json.dumps({
                    "error": "authentication_required",
                    "message": "Include your ThinkNEO API key as Bearer token.",
                    "get_key": "https://thinkneo.app/pricing",
                }, indent=2)

            key_h = hash_key(token)
            balance = get_tnc_balance(key_h)

            if balance < cost:
                return json.dumps({
                    "error": "insufficient_credits",
                    "message": f"This tool costs {cost} TNC. Your balance: {balance:.1f} TNC.",
                    "top_up": "https://thinkneo.app/pricing",
                    "balance": balance,
                }, indent=2)

            # Execute the tool
            result = fn(*args, **kwargs)

            # Deduct credits
            tool_name = fn.__name__
            ip = get_client_ip()
            deduct_tnc(key_h, cost, tool_name, product)

            # Append usage footer
            try:
                if isinstance(result, str):
                    parsed = json.loads(result)
                    if isinstance(parsed, dict):
                        usage = get_monthly_usage(key_h, product)
                        parsed["_billing"] = {
                            "tnc_charged": cost,
                            "tnc_balance": balance - cost,
                            "product": product,
                            **usage,
                        }
                        return json.dumps(parsed, indent=2, ensure_ascii=False)
            except (json.JSONDecodeError, TypeError):
                pass

            return result

        return wrapper

    return decorator


def free_tool(fn: Callable) -> Callable:
    """Decorator for tools that don't charge TNC (demo/public tools)."""

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper
