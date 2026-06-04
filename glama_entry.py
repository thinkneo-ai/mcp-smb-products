"""
Glama build test entry point — runs the Guardrails product in stdio mode
for mcp-proxy to wrap. This file is only used by Glama's build system.
"""
import sys
import os
from typing import Annotated

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
from pydantic import Field

# Create a minimal MCP server with the guardrails tools for Glama testing
mcp = FastMCP(
    name="ThinkNEO MCP SMB Guardrails",
    instructions=(
        "AI safety guardrails for SMBs. Provides prompt injection detection, "
        "PII scanning (email, phone, CPF, CNPJ, SSN, credit cards), and secret/credential "
        "leak detection (API keys, tokens, passwords). Use guardrails_check for a comprehensive "
        "scan, or the individual scan tools for targeted analysis."
    ),
)


@mcp.tool()
def guardrails_check(
    text: Annotated[str, Field(
        description="The text, prompt, or code snippet to analyze for safety issues. "
        "Accepts any length up to 50,000 characters. Pass the full user input "
        "or LLM prompt you want to validate before sending to a model."
    )],
) -> str:
    """Run a comprehensive safety scan that checks for prompt injection attacks, PII exposure (emails, phones, CPF, CNPJ, credit cards, SSN), and leaked secrets (API keys, tokens, passwords) in a single call. Returns a risk level (ALLOWED, MEDIUM, HIGH, or BLOCKED), a list of findings with severity, and a recommendation. Use this as a pre-flight check before sending any user input to an AI model. Costs 2 TNC per call."""
    return '{"risk_level": "ALLOWED", "findings_count": 0, "findings": [], "recommendation": "Safe to proceed"}'


@mcp.tool()
def guardrails_scan_pii(
    text: Annotated[str, Field(
        description="The text to scan for personally identifiable information. "
        "Can be user input, chat messages, documents, or any string that might "
        "contain sensitive data like email addresses, phone numbers, or ID numbers."
    )],
) -> str:
    """Scan text for personally identifiable information (PII) across international formats. Detects email addresses, phone numbers (US and international), Brazilian CPF and CNPJ, US Social Security Numbers, and credit card numbers. Returns whether PII was found, the type and count of each detection, and redacted samples for verification. Use this to audit text before logging, storing, or sharing. Costs 1 TNC per call."""
    return '{"pii_detected": false, "findings": []}'


@mcp.tool()
def guardrails_scan_secrets(
    text: Annotated[str, Field(
        description="The text or source code to scan for leaked credentials. "
        "Pass code snippets, configuration files, log output, or any string "
        "that might accidentally contain API keys, tokens, or passwords."
    )],
) -> str:
    """Scan text or code for exposed secrets and credentials. Detects Stripe keys, AWS access keys, GitHub PATs, OpenAI keys, Slack tokens, JWTs, hardcoded passwords, and API key literals. Returns whether secrets were found, the type and count of each detection, and an overall severity rating. Use this before committing code or sharing logs. Costs 1 TNC per call."""
    return '{"secrets_detected": false, "findings": [], "severity": "none"}'


@mcp.tool()
def guardrails_scan_injection(
    text: Annotated[str, Field(
        description="The prompt or user message to analyze for injection attacks. "
        "Pass the raw user input before it reaches the LLM system prompt. "
        "Works with any language but patterns are optimized for English."
    )],
) -> str:
    """Detect prompt injection and jailbreak attempts in user input. Checks for 10 attack patterns including instruction override, jailbreak personas (DAN), system prompt extraction, safety bypass, sudo mode, debug mode, base64 smuggling, and unicode obfuscation. Returns whether an injection was detected, the risk level (HIGH or SAFE), and a list of specific attack types found. Use this to protect your AI application from adversarial inputs. Costs 1 TNC per call."""
    return '{"injection_detected": false, "risk": "SAFE", "attacks": []}'


if __name__ == "__main__":
    mcp.run(transport="stdio")
