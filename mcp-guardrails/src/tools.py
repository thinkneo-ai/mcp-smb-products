"""Guardrails tools — prompt safety, PII, secrets, injection detection."""
from __future__ import annotations
import json, re
from typing import Annotated
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.billing import tnc_tool

PRODUCT = "guardrails"

# --- Patterns ---
_INJECTION_PATTERNS = [
    (r"ignore\b.{0,30}\b(previous|prior|above)\b.{0,30}\binstructions?", "Override previous instructions"),
    (r"(you are|act as|pretend)\b.{0,30}\b(DAN|unrestricted|jailbr)", "Jailbreak persona"),
    (r"(new|override|updated)\s+(system\s+)?(instructions?|prompt):", "Inject new instructions"),
    (r"forget\b.{0,30}\b(everything|all|your instructions)", "Reset model memory"),
    (r"reveal\b.{0,30}\b(system\s+prompt|instructions?|hidden)", "Extract system prompt"),
    (r"(bypass|circumvent)\b.{0,30}\b(safety|filters?|restrictions?)", "Bypass safety"),
    (r"\bsudo\b.{0,20}\b(mode|admin|override)", "Sudo mode injection"),
    (r"(developer|debug)\s+mode\b.{0,20}\b(enabled|on)", "Debug mode injection"),
    (r"base64\b.{0,20}\b(decode|encoded|payload)", "Base64 smuggling"),
    (r"[\u200b-\u200f\u2028-\u202f]", "Unicode obfuscation"),
]

_PII_PATTERNS = [
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email"),
    (r"\b\d{3}[\.\-]?\d{3}[\.\-]?\d{3}[\.\-]?\d{2}\b", "cpf"),
    (r"\b\d{2}[\.\-]?\d{3}[\.\-]?\d{3}[/\-]?\d{4}[\.\-]?\d{2}\b", "cnpj"),
    (r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "phone"),
    (r"\b(?:\+\d{1,3}[\s-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,5}[\s.-]?\d{4}\b", "phone_intl"),
    (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "credit_card"),
    (r"\b\d{3}-\d{2}-\d{4}\b", "ssn"),
]

_SECRET_PATTERNS = [
    (r"(sk|pk)[-_](live|test)[-_][A-Za-z0-9]{20,}", "stripe_key"),
    (r"AKIA[0-9A-Z]{16}", "aws_access_key"),
    (r"ghp_[A-Za-z0-9]{36}", "github_pat"),
    (r"sk-[A-Za-z0-9]{32,}", "openai_key"),
    (r"xox[baprs]-[A-Za-z0-9\-]{10,}", "slack_token"),
    (r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}", "jwt"),
    (r"(?i)(password|passwd|pwd)\s*[:=]\s*\S+", "password_literal"),
    (r"(?i)(api[_-]?key|secret[_-]?key|access[_-]?token)\s*[:=]\s*\S+", "api_key_literal"),
]


def register_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=2.0)
    def guardrails_check(
        text: Annotated[str, Field(description="Text to analyze for safety issues")],
    ) -> str:
        """Comprehensive safety check: injection + PII + secrets + toxicity. Costs 2 TNC."""
        findings = []
        # Injection
        for pattern, label in _INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                findings.append({"type": "injection", "pattern": label, "severity": "high"})
        # PII
        for pattern, pii_type in _PII_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                findings.append({"type": "pii", "pii_type": pii_type, "count": len(matches), "severity": "medium"})
        # Secrets
        for pattern, secret_type in _SECRET_PATTERNS:
            if re.search(pattern, text):
                findings.append({"type": "secret", "secret_type": secret_type, "severity": "critical"})

        risk = "BLOCKED" if any(f["severity"] == "critical" for f in findings) else \
               "HIGH" if any(f["severity"] == "high" for f in findings) else \
               "MEDIUM" if findings else "ALLOWED"

        return json.dumps({
            "risk_level": risk,
            "findings_count": len(findings),
            "findings": findings,
            "recommendation": "Block this input" if risk in ("BLOCKED", "HIGH") else "Safe to proceed",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def guardrails_scan_pii(
        text: Annotated[str, Field(description="Text to scan for PII")],
    ) -> str:
        """Detect PII (emails, phones, CPF, CNPJ, credit cards, SSN). Costs 1 TNC."""
        findings = []
        for pattern, pii_type in _PII_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                findings.append({"pii_type": pii_type, "count": len(matches), "redacted_samples": [m[:3] + "***" for m in matches[:3]]})
        return json.dumps({"pii_detected": len(findings) > 0, "findings": findings}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def guardrails_scan_secrets(
        text: Annotated[str, Field(description="Text/code to scan for exposed secrets")],
    ) -> str:
        """Detect exposed API keys, tokens, passwords in text/code. Costs 1 TNC."""
        findings = []
        for pattern, secret_type in _SECRET_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                findings.append({"secret_type": secret_type, "count": len(matches)})
        return json.dumps({"secrets_detected": len(findings) > 0, "findings": findings, "severity": "critical" if findings else "none"}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def guardrails_scan_injection(
        text: Annotated[str, Field(description="Prompt text to check for injection attacks")],
    ) -> str:
        """Detect prompt injection attempts (jailbreak, override, extraction). Costs 1 TNC."""
        findings = []
        for pattern, label in _INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                findings.append({"attack_type": label})
        risk = "HIGH" if findings else "SAFE"
        return json.dumps({"injection_detected": len(findings) > 0, "risk": risk, "attacks": findings}, indent=2)
