"""
Database — shared PostgreSQL connection pool for all PME MCP products.
"""

from __future__ import annotations

import hashlib
import logging
import threading
from typing import Any, Optional

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

logger = logging.getLogger(__name__)

_pool: Optional[ConnectionPool] = None
_pool_lock = threading.Lock()
_conninfo: str = ""


def init_pool(conninfo: str) -> None:
    """Initialize the connection pool with the given conninfo string."""
    global _conninfo
    _conninfo = conninfo


def _get_pool() -> ConnectionPool:
    global _pool
    if _pool is not None:
        return _pool
    with _pool_lock:
        if _pool is not None:
            return _pool
        _pool = ConnectionPool(
            conninfo=_conninfo,
            min_size=1,
            max_size=10,
            kwargs={"row_factory": dict_row, "autocommit": True},
            timeout=30.0,
            max_idle=300.0,
            max_lifetime=1800.0,
            num_workers=1,
        )
        logger.info("Connection pool initialized")
        return _pool


def get_conn():
    return _get_pool().connection()


def hash_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()


def log_tool_call(
    key_hash: str,
    tool_name: str,
    product: str,
    tnc_cost: float = 1.0,
    ip: Optional[str] = None,
) -> None:
    """Log a tool call and deduct TNC credits."""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO product_usage_log (key_hash, tool_name, product, tnc_cost, ip)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (key_hash, tool_name, product, tnc_cost, ip),
                )
    except Exception as exc:
        logger.warning("DB log_tool_call failed: %s", exc)


def get_tnc_balance(key_hash: str) -> float:
    """Get remaining TNC balance for a key."""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT tnc_balance FROM tnc_accounts WHERE key_hash = %s",
                    (key_hash,),
                )
                row = cur.fetchone()
                return float(row["tnc_balance"]) if row else 0.0
    except Exception:
        return 0.0


def deduct_tnc(key_hash: str, amount: float, tool_name: str, product: str) -> bool:
    """Deduct TNC credits. Returns True if successful, False if insufficient."""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE tnc_accounts
                    SET tnc_balance = tnc_balance - %s,
                        last_used_at = NOW()
                    WHERE key_hash = %s AND tnc_balance >= %s
                    RETURNING tnc_balance
                    """,
                    (amount, key_hash, amount),
                )
                row = cur.fetchone()
                if row:
                    log_tool_call(key_hash, tool_name, product, amount)
                    return True
                return False
    except Exception as exc:
        logger.warning("TNC deduction failed: %s", exc)
        return False


def get_monthly_usage(key_hash: str, product: str) -> dict[str, Any]:
    """Get usage stats for a specific product."""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*) as calls, COALESCE(SUM(tnc_cost), 0) as tnc_spent
                    FROM product_usage_log
                    WHERE key_hash = %s AND product = %s
                      AND called_at >= date_trunc('month', NOW())
                    """,
                    (key_hash, product),
                )
                row = cur.fetchone()
                return {
                    "calls_this_month": row["calls"] if row else 0,
                    "tnc_spent_this_month": float(row["tnc_spent"]) if row else 0.0,
                }
    except Exception:
        return {"calls_this_month": 0, "tnc_spent_this_month": 0.0}


def db_healthy() -> bool:
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                return True
    except Exception:
        return False
