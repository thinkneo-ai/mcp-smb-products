"""
ThinkNEO MCP SMB Guardrails — PME Product
Detect prompt injection, PII leaks, secrets, and toxic content.
"""
from __future__ import annotations
import logging, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from mcp.server.fastmcp import FastMCP
from shared.config import BaseSettings
from shared.server_factory import create_product_mcp
from .tools import register_tools

class Settings(BaseSettings):
    def __init__(self):
        super().__init__(product_name="SMB Guardrails", default_port=8101)

settings = Settings()

INSTRUCTIONS = (
    "You are connected to ThinkNEO MCP SMB Guardrails — AI safety for SMEs. "
    "Available tools:\n"
    "- guardrails_check: Comprehensive prompt safety check (injection + PII + secrets + toxicity)\n"
    "- guardrails_scan_pii: Detect PII in text (emails, phones, CPF, CNPJ, credit cards, etc.)\n"
    "- guardrails_scan_secrets: Detect exposed secrets (API keys, tokens, passwords)\n"
    "- guardrails_scan_injection: Detect prompt injection attempts\n"
    "\nAll tools consume TNC credits. Get credits at https://thinkneo.app/pricing"
)

mcp, app = create_product_mcp(
    settings=settings,
    instructions=INSTRUCTIONS,
    register_tools=register_tools,
    version="1.0.0",
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host=settings.host, port=settings.port, workers=1)
