"""Trust Score tools — governance evaluation, badges, recommendations."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.billing import tnc_tool

PRODUCT = "trust-score"

CATEGORIES = [
    "data_privacy", "model_governance", "access_control", "audit_trail",
    "bias_fairness", "transparency", "security", "compliance",
    "incident_response", "documentation",
]

def _score_to_badge(score: int) -> str:
    if score >= 90: return "Platinum"
    if score >= 75: return "Gold"
    if score >= 50: return "Silver"
    return "Bronze"

def register_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=5.0)
    def trust_evaluate(
        has_guardrails: Annotated[bool, Field(description="Do you use AI guardrails?")] = False,
        has_audit_log: Annotated[bool, Field(description="Do you log AI decisions?")] = False,
        has_access_control: Annotated[bool, Field(description="Is AI access role-based?")] = False,
        has_data_policy: Annotated[bool, Field(description="Do you have a data handling policy?")] = False,
        has_monitoring: Annotated[bool, Field(description="Do you monitor AI outputs?")] = False,
        has_incident_plan: Annotated[bool, Field(description="Do you have an AI incident response plan?")] = False,
        has_bias_testing: Annotated[bool, Field(description="Do you test for AI bias?")] = False,
        has_documentation: Annotated[bool, Field(description="Is your AI usage documented?")] = False,
        has_compliance: Annotated[bool, Field(description="Are you compliant with regulations (LGPD/GDPR)?")] = False,
        has_transparency: Annotated[bool, Field(description="Do you disclose AI use to users?")] = False,
    ) -> str:
        """Evaluate your AI governance posture. Costs 5 TNC."""
        answers = [has_guardrails, has_audit_log, has_access_control, has_data_policy,
                   has_monitoring, has_incident_plan, has_bias_testing, has_documentation,
                   has_compliance, has_transparency]
        scores = {}
        for cat, ans in zip(CATEGORIES, answers):
            scores[cat] = 10 if ans else 2
        total = sum(scores.values())
        badge = _score_to_badge(total)
        return json.dumps({
            "trust_score": total,
            "max_score": 100,
            "badge": badge,
            "category_scores": scores,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def trust_get_badge(
        score: Annotated[int, Field(description="Trust score (0-100)")],
    ) -> str:
        """Get trust badge for a given score. Costs 1 TNC."""
        badge = _score_to_badge(score)
        colors = {"Platinum": "#E5E4E2", "Gold": "#FFD700", "Silver": "#C0C0C0", "Bronze": "#CD7F32"}
        return json.dumps({
            "score": score,
            "badge": badge,
            "color": colors[badge],
            "embed_url": f"https://mcp.thinkneo.app/trust-score/badge/{badge.lower()}.svg",
            "description": f"ThinkNEO AI Trust Score: {score}/100 — {badge} tier",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=3.0)
    def trust_recommendations(
        current_score: Annotated[int, Field(description="Your current trust score")],
        weakest_categories: Annotated[Optional[str], Field(description="Comma-separated weak categories")] = None,
    ) -> str:
        """Get actionable recommendations to improve your score. Costs 3 TNC."""
        recs = {
            "data_privacy": "Implement data classification and PII detection before sending to AI models.",
            "model_governance": "Define approved model list and enforce via policy engine.",
            "access_control": "Implement RBAC for AI tool access. Use API keys per team/project.",
            "audit_trail": "Log all AI interactions with timestamps, user, model, and outcome.",
            "bias_fairness": "Run periodic bias audits on AI outputs across demographic groups.",
            "transparency": "Add AI disclosure notices where AI-generated content is used.",
            "security": "Enable guardrails, scan for prompt injection and secrets exposure.",
            "compliance": "Map AI usage to regulatory requirements (LGPD Art. 20, GDPR Art. 22).",
            "incident_response": "Create runbook for AI failures: hallucinations, data leaks, bias incidents.",
            "documentation": "Document all AI systems: purpose, data flows, risk assessments.",
        }
        weak = [c.strip() for c in (weakest_categories or "").split(",") if c.strip()] or CATEGORIES[:5]
        recommendations = [{"category": c, "action": recs.get(c, "Improve this area.")} for c in weak if c in recs]
        return json.dumps({
            "current_score": current_score,
            "target_score": min(current_score + 20, 100),
            "recommendations": recommendations,
            "estimated_improvement": f"+{min(20, 100 - current_score)} points",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def trust_history(
        periods: Annotated[int, Field(description="Number of historical periods to show")] = 6,
    ) -> str:
        """View trust score history. Costs 1 TNC."""
        return json.dumps({
            "history": [],
            "note": "Score history will populate after your first evaluation. Run trust_evaluate to start.",
        }, indent=2)
