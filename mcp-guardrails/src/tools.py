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
        text: Annotated[str, Field(
            description="The text, prompt, or code snippet to analyze for safety issues. "
            "Accepts any length up to 50,000 characters. Pass the full user input "
            "or LLM prompt you want to validate before sending to a model."
        )],
    ) -> str:
        """Run a comprehensive safety scan that checks for prompt injection attacks, PII exposure (emails, phones, CPF, CNPJ, credit cards, SSN), and leaked secrets (API keys, tokens, passwords) in a single call. Returns a risk level (ALLOWED, MEDIUM, HIGH, or BLOCKED), a list of findings with severity, and a recommendation. Use this as a pre-flight check before sending any user input to an AI model. Costs 2 TNC per call."""
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
        text: Annotated[str, Field(
            description="The text to scan for personally identifiable information. "
            "Can be user input, chat messages, documents, or any string that might "
            "contain sensitive data like email addresses, phone numbers, or ID numbers."
        )],
    ) -> str:
        """Scan text for personally identifiable information (PII) across international formats. Detects email addresses, phone numbers (US and international), Brazilian CPF and CNPJ, US Social Security Numbers, and credit card numbers. Returns whether PII was found, the type and count of each detection, and redacted samples for verification. Use this to audit text before logging, storing, or sharing. Costs 1 TNC per call."""
        findings = []
        for pattern, pii_type in _PII_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                findings.append({"pii_type": pii_type, "count": len(matches), "redacted_samples": [m[:3] + "***" for m in matches[:3]]})
        return json.dumps({"pii_detected": len(findings) > 0, "findings": findings}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def guardrails_scan_secrets(
        text: Annotated[str, Field(
            description="The text or source code to scan for leaked credentials. "
            "Pass code snippets, configuration files, log output, or any string "
            "that might accidentally contain API keys, tokens, or passwords."
        )],
    ) -> str:
        """Scan text or code for exposed secrets and credentials. Detects Stripe keys, AWS access keys, GitHub PATs, OpenAI keys, Slack tokens, JWTs, hardcoded passwords, and API key literals. Returns whether secrets were found, the type and count of each detection, and an overall severity rating (critical if secrets found, none otherwise). Use this before committing code or sharing logs. Costs 1 TNC per call."""
        findings = []
        for pattern, secret_type in _SECRET_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                findings.append({"secret_type": secret_type, "count": len(matches)})
        return json.dumps({"secrets_detected": len(findings) > 0, "findings": findings, "severity": "critical" if findings else "none"}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def guardrails_scan_injection(
        text: Annotated[str, Field(
            description="The prompt or user message to analyze for injection attacks. "
            "Pass the raw user input before it reaches the LLM system prompt. "
            "Works with any language but patterns are optimized for English."
        )],
    ) -> str:
        """Detect prompt injection and jailbreak attempts in user input. Checks for 10 attack patterns including instruction override, jailbreak personas (DAN), system prompt extraction, safety bypass, sudo mode, debug mode, base64 smuggling, and unicode obfuscation. Returns whether an injection was detected, the risk level (HIGH or SAFE), and a list of specific attack types found. Use this to protect your AI application from adversarial inputs. Costs 1 TNC per call."""
        findings = []
        for pattern, label in _INJECTION_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                findings.append({"attack_type": label})
        risk = "HIGH" if findings else "SAFE"
        return json.dumps({"injection_detected": len(findings) > 0, "risk": risk, "attacks": findings}, indent=2)
