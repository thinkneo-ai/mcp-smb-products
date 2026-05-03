"""
Base configuration for ThinkNEO PME MCP products.
Each product server imports this and extends with product-specific settings.
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional


class BaseSettings:
    def __init__(self, product_name: str, default_port: int = 8090) -> None:
        self.product_name = product_name
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", str(default_port)))
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()

        # TNC Billing
        self.tnc_api_url: str = os.getenv("TNC_API_URL", "http://127.0.0.1:8081")
        self.tnc_product_id: str = os.getenv("TNC_PRODUCT_ID", product_name)

        # Database (shared PostgreSQL)
        self.db_host: str = os.getenv("MCP_DB_HOST", "172.17.0.1")
        self.db_port: int = int(os.getenv("MCP_DB_PORT", "5432"))
        self.db_name: str = os.getenv("MCP_DB_NAME", "thinkneo_mcp")
        self.db_user: str = os.getenv("MCP_DB_USER", "mcp_user")
        self.db_password: str = os.getenv("MCP_DB_PASSWORD", "")

        # Redis
        self.redis_url: str = os.getenv("MCP_REDIS_URL", "redis://redis:6379/0")

        # CORS
        self.allowed_origins_raw: str = os.getenv(
            "ALLOWED_ORIGINS",
            "https://claude.ai,https://chatgpt.com,https://copilot.microsoft.com,https://thinkneo.app",
        )

        # Public URL
        self.public_url: str = os.getenv("PUBLIC_URL", f"https://mcp.thinkneo.app/{product_name}")

    @property
    def allowed_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins_raw.split(",") if o.strip()]

    @property
    def conninfo(self) -> str:
        return (
            f"host={self.db_host} port={self.db_port} "
            f"dbname={self.db_name} user={self.db_user} password={self.db_password}"
        )
