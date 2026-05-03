"""ThinkSecure tools — input sanitization, output validation, audit logging."""
from __future__ import annotations
import json, re, uuid
from datetime import datetime, timezone
from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.billing import tnc_tool

PRODUCT = "thinksecure"

_audit_log: list[dict] = []

_DANGEROUS_PATTERNS = [
    (r"<script[^>]*>.*?</script>", "xss_script"),
    (r"javascript:", "xss_protocol"),
    (r"on\w+\s*=", "xss_event_handler"),
    (r"(\b(DROP|DELETE|ALTER|TRUNCATE)\b\s+(TABLE|DATABASE|INDEX))", "sql_injection"),
    (r";\s*(DROP|DELETE|INSERT|UPDATE|ALTER)", "sql_injection"),
    (r"(\.\./){2,}", "path_traversal"),
    (r"(rm\s+-rf|sudo\s+rm|chmod\s+777)", "command_injection"),
]


def register_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def secure_sanitize_input(
        text: Annotated[str, Field(description="User input to sanitize before sending to AI")],
        strip_html: Annotated[bool, Field(description="Remove HTML tags")] = True,
        strip_urls: Annotated[bool, Field(description="Remove URLs")] = False,
        max_length: Annotated[int, Field(description="Maximum allowed length")] = 10000,
    ) -> str:
        """Sanitize user input for AI consumption. Costs 1 TNC."""
        sanitized = text
        threats = []
        for pattern, threat_type in _DANGEROUS_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE | re.DOTALL):
                threats.append(threat_type)
                sanitized = re.sub(pattern, "[BLOCKED]", sanitized, flags=re.IGNORECASE | re.DOTALL)
        if strip_html:
            sanitized = re.sub(r"<[^>]+>", "", sanitized)
        if strip_urls:
            sanitized = re.sub(r"https?://\S+", "[URL_REMOVED]", sanitized)
        sanitized = sanitized[:max_length]
        return json.dumps({
            "sanitized": sanitized,
            "threats_found": threats,
            "original_length": len(text),
            "sanitized_length": len(sanitized),
            "safe": len(threats) == 0,
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def secure_validate_output(
        ai_output: Annotated[str, Field(description="AI-generated output to validate")],
        check_pii: Annotated[bool, Field(description="Check for PII in output")] = True,
        check_harmful: Annotated[bool, Field(description="Check for harmful content")] = True,
    ) -> str:
        """Validate AI output before returning to user. Costs 1 TNC."""
        issues = []
        if check_pii:
            pii_patterns = [
                (r"\b\d{3}[-.]?\d{3}[-.]?\d{3}[-.]?\d{2}\b", "cpf"),
                (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.\w{2,}\b", "email"),
                (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "credit_card"),
            ]
            for pattern, pii_type in pii_patterns:
                if re.search(pattern, ai_output):
                    issues.append({"type": "pii_leak", "pii_type": pii_type, "severity": "high"})
        if check_harmful:
            harmful = [r"\b(kill|harm|attack|exploit)\b.*\b(how to|instructions|steps)\b"]
            for pattern in harmful:
                if re.search(pattern, ai_output, re.IGNORECASE):
                    issues.append({"type": "harmful_content", "severity": "critical"})
        return json.dumps({
            "valid": len(issues) == 0,
            "issues": issues,
            "output_length": len(ai_output),
            "recommendation": "Block" if any(i["severity"] == "critical" for i in issues) else "Redact" if issues else "Allow",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=0.5)
    def secure_audit_log(
        action: Annotated[str, Field(description="Action performed (e.g., 'query', 'generate', 'classify')")],
        user_id: Annotated[str, Field(description="User who performed the action")],
        model: Annotated[Optional[str], Field(description="AI model used")] = None,
        input_summary: Annotated[Optional[str], Field(description="Brief summary of input (no PII)")] = None,
        output_summary: Annotated[Optional[str], Field(description="Brief summary of output")] = None,
        outcome: Annotated[str, Field(description="Outcome: 'success', 'blocked', 'error'")] = "success",
    ) -> str:
        """Log an AI interaction for compliance. Costs 0.5 TNC."""
        entry = {
            "audit_id": str(uuid.uuid4())[:12],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "user_id": user_id,
            "model": model,
            "input_summary": input_summary,
            "output_summary": output_summary,
            "outcome": outcome,
        }
        _audit_log.append(entry)
        return json.dumps({"logged": True, "audit_id": entry["audit_id"]}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def secure_check_permissions(
        user_id: Annotated[str, Field(description="User ID to check")],
        action: Annotated[str, Field(description="Action: 'query', 'generate', 'admin', 'export'")],
        resource: Annotated[str, Field(description="Resource: model name or tool name")],
    ) -> str:
        """Check if user has permission for an AI action. Costs 1 TNC."""
        # Default: all allowed (configure via dashboard)
        return json.dumps({
            "allowed": True,
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "note": "Default policy: allow-all. Configure RBAC at https://thinkneo.app/settings/security",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=3.0)
    def secure_export_audit(
        format: Annotated[str, Field(description="Export format: 'json', 'csv'")] = "json",
        limit: Annotated[int, Field(description="Max entries to export")] = 100,
    ) -> str:
        """Export audit log for compliance. Costs 3 TNC."""
        entries = _audit_log[-limit:]
        if format == "csv":
            header = "audit_id,timestamp,action,user_id,model,outcome"
            rows = [f"{e['audit_id']},{e['timestamp']},{e['action']},{e['user_id']},{e.get('model','')},{e['outcome']}" for e in entries]
            csv_content = header + "\n" + "\n".join(rows)
            return json.dumps({"format": "csv", "entries": len(entries), "content": csv_content}, indent=2)
        return json.dumps({"format": "json", "entries": len(entries), "data": entries}, indent=2)
