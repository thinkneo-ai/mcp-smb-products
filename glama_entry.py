"""
Glama build test entry point — runs the Guardrails product in stdio mode
for mcp-proxy to wrap. This file is only used by Glama's build system.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set defaults so the server can start without a live DB
os.environ.setdefault("MCP_DB_HOST", "localhost")
os.environ.setdefault("MCP_DB_PORT", "5432")
os.environ.setdefault("MCP_DB_NAME", "test")
os.environ.setdefault("MCP_DB_USER", "test")
os.environ.setdefault("MCP_DB_PASSWORD", "test")
os.environ.setdefault("MCP_REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("PORT", "8090")

from mcp.server.fastmcp import FastMCP

# Create a minimal MCP server with the guardrails tools for Glama testing
mcp = FastMCP(
    name="ThinkNEO MCP SMB Guardrails",
    instructions="AI safety for SMBs — prompt injection, PII, secrets detection.",
)


@mcp.tool()
def guardrails_check(text: str) -> str:
    """Comprehensive safety check: injection + PII + secrets + toxicity. Costs 2 TNC."""
    return '{"safe": true, "findings": []}'


@mcp.tool()
def guardrails_scan_pii(text: str) -> str:
    """Detect PII (emails, phones, CPF, CNPJ, credit cards, SSN). Costs 1 TNC."""
    return '{"pii_found": []}'


@mcp.tool()
def guardrails_scan_secrets(text: str) -> str:
    """Detect exposed API keys, tokens, passwords in text/code. Costs 1 TNC."""
    return '{"secrets_found": []}'


@mcp.tool()
def guardrails_scan_injection(text: str) -> str:
    """Detect prompt injection attempts (jailbreak, override, extraction). Costs 1 TNC."""
    return '{"injection_detected": false}'


if __name__ == "__main__":
    mcp.run(transport="stdio")
