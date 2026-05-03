"""
Server Factory — creates a standard MCP server for any PME product.
"""

from __future__ import annotations

import logging
import sys
from typing import Callable, Optional

from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse

from .auth import BearerTokenMiddleware
from .config import BaseSettings
from .database import init_pool


def create_product_mcp(
    settings: BaseSettings,
    instructions: str,
    register_tools: Callable[[FastMCP], None],
    version: str = "1.0.0",
    landing_html: Optional[str] = None,
) -> tuple[FastMCP, any]:
    """
    Create a fully configured MCP server for a PME product.
    Returns (mcp_instance, asgi_app).
    """
    # Init database pool
    init_pool(settings.conninfo)

    # Logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        stream=sys.stdout,
    )
    logger = logging.getLogger(settings.product_name)

    # Create FastMCP
    mcp = FastMCP(
        name=f"ThinkNEO {settings.product_name}",
        instructions=instructions,
        stateless_http=True,
        streamable_http_path="/mcp",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level,
    )
    mcp._mcp_server.version = version

    # Register product-specific tools
    register_tools(mcp)

    # Build ASGI app with middleware stack
    mcp_starlette = mcp.streamable_http_app()

    # Landing page middleware
    class LandingPageMiddleware:
        def __init__(self, app):
            self.app = app

        async def __call__(self, scope, receive, send):
            if scope["type"] == "http":
                path = scope.get("path", "")
                method = scope.get("method", "GET")
                if path in ("/mcp/docs", "/mcp/docs/") and method == "GET":
                    html = landing_html or _default_landing(settings)
                    response = HTMLResponse(html, status_code=200)
                    await response(scope, receive, send)
                    return
            await self.app(scope, receive, send)

    _with_auth = BearerTokenMiddleware(mcp_starlette)
    _with_landing = LandingPageMiddleware(_with_auth)

    app = CORSMiddleware(
        app=_with_landing,
        allow_origins=settings.allowed_origins or ["*"],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    logger.info(
        "ThinkNEO %s MCP Server ready on %s:%d",
        settings.product_name,
        settings.host,
        settings.port,
    )

    return mcp, app


def _default_landing(settings: BaseSettings) -> str:
    return f"""<!DOCTYPE html>
<html><head><title>ThinkNEO {settings.product_name} MCP</title>
<style>
body {{ font-family: system-ui; max-width: 700px; margin: 50px auto; padding: 20px; background: #0a0a0a; color: #e0e0e0; }}
h1 {{ color: #00d4aa; }}
code {{ background: #1a1a2e; padding: 2px 8px; border-radius: 4px; }}
.badge {{ display: inline-block; background: #00d4aa; color: #000; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
</style></head>
<body>
<h1>ThinkNEO {settings.product_name}</h1>
<p class="badge">MCP SMB Product</p>
<p>Remote MCP server for <strong>{settings.product_name}</strong>.</p>
<h3>Connect</h3>
<pre><code>{{
  "mcpServers": {{
    "thinkneo-{settings.product_name.lower().replace(' ', '-')}": {{
      "url": "{settings.public_url}/mcp",
      "transport": "streamable-http",
      "headers": {{
        "Authorization": "Bearer YOUR_TNC_API_KEY"
      }}
    }}
  }}
}}</code></pre>
<h3>Billing</h3>
<p>All calls consume <strong>TNC (ThinkNEO Credits)</strong>. Get credits at <a href="https://thinkneo.app/pricing" style="color:#00d4aa">thinkneo.app/pricing</a>.</p>
<p>Free trial: 30 days, 1000 requests.</p>
</body></html>"""
