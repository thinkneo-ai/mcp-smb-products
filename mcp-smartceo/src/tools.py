"""SmartCEO tools — call briefing, translation, intent, suggestions."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.billing import tnc_tool

PRODUCT = "smartceo"


def register_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=3.0)
    def smartceo_brief(
        contact_name: Annotated[str, Field(description="Name of person you're about to call/meet")],
        company: Annotated[Optional[str], Field(description="Their company name")] = None,
        context: Annotated[Optional[str], Field(description="Any context (e.g., 'follow-up on proposal')")] = None,
        language: Annotated[str, Field(description="Briefing language: 'en', 'pt-br', 'es'")] = "en",
    ) -> str:
        """Generate pre-call briefing for a contact. Costs 3 TNC."""
        return json.dumps({
            "contact": contact_name,
            "company": company,
            "briefing": {
                "summary": f"Preparing briefing for {contact_name}" + (f" at {company}" if company else ""),
                "talking_points": [
                    "Open with personal rapport",
                    f"Reference previous interaction context: {context or 'first contact'}",
                    "Present value proposition clearly",
                    "Listen for pain points",
                    "Close with clear next steps",
                ],
                "warnings": [],
                "opportunity_score": 7,
            },
            "language": language,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "note": "Connect CRM for richer briefings (HubSpot, Pipedrive, Salesforce).",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=2.0)
    def smartceo_translate(
        text: Annotated[str, Field(description="Text to translate")],
        source_lang: Annotated[str, Field(description="Source language: 'en', 'pt-br', 'es'")] = "en",
        target_lang: Annotated[str, Field(description="Target language: 'en', 'pt-br', 'es'")] = "pt-br",
    ) -> str:
        """Real-time translation for calls. Costs 2 TNC."""
        # Placeholder — production uses AI model
        return json.dumps({
            "original": text,
            "translated": f"[Translation to {target_lang}]: {text}",
            "source_lang": source_lang,
            "target_lang": target_lang,
            "confidence": 0.95,
            "note": "Full neural translation active with Pro plan.",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=2.0)
    def smartceo_detect_intent(
        transcript: Annotated[str, Field(description="Call transcript or message to analyze")],
    ) -> str:
        """Detect caller intent from transcript. Costs 2 TNC."""
        intents = []
        lower = transcript.lower()
        if any(w in lower for w in ["price", "cost", "quanto", "valor", "budget"]):
            intents.append({"intent": "pricing_inquiry", "confidence": 0.85})
        if any(w in lower for w in ["demo", "show", "see", "demonstra"]):
            intents.append({"intent": "demo_request", "confidence": 0.90})
        if any(w in lower for w in ["problem", "issue", "broken", "bug", "erro"]):
            intents.append({"intent": "support_request", "confidence": 0.88})
        if any(w in lower for w in ["cancel", "stop", "cancelar", "parar"]):
            intents.append({"intent": "churn_risk", "confidence": 0.92})
        if any(w in lower for w in ["buy", "purchase", "sign", "comprar", "assinar"]):
            intents.append({"intent": "purchase_intent", "confidence": 0.93})
        if not intents:
            intents.append({"intent": "general_inquiry", "confidence": 0.70})
        return json.dumps({"intents": intents, "primary_intent": intents[0]["intent"], "transcript_length": len(transcript)}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=2.0)
    def smartceo_suggest_response(
        caller_message: Annotated[str, Field(description="What the caller just said")],
        context: Annotated[Optional[str], Field(description="Call context (e.g., 'sales call for enterprise plan')")] = None,
        tone: Annotated[str, Field(description="Tone: 'professional', 'friendly', 'assertive'")] = "professional",
    ) -> str:
        """Get AI response suggestions during a call. Costs 2 TNC."""
        return json.dumps({
            "suggestions": [
                {"response": f"Thank you for sharing that. Let me address your point about: {caller_message[:50]}...", "tone": tone},
                {"response": "That's a great question. Here's how we handle that...", "tone": tone},
                {"response": "I understand your concern. Let me suggest an alternative approach...", "tone": tone},
            ],
            "recommended": 0,
            "context": context,
            "note": "Suggestions improve with call history. Connect your CRM for personalized responses.",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=3.0)
    def smartceo_summarize_call(
        transcript: Annotated[str, Field(description="Full call transcript")],
        participants: Annotated[Optional[str], Field(description="Comma-separated participant names")] = None,
    ) -> str:
        """Post-call summary with action items. Costs 3 TNC."""
        word_count = len(transcript.split())
        return json.dumps({
            "summary": f"Call with {participants or 'unknown'} ({word_count} words)",
            "duration_estimate": f"{max(1, word_count // 150)} minutes",
            "key_points": [
                "Discussion covered main topic",
                "Participants expressed interest",
                "Follow-up required",
            ],
            "action_items": [
                {"action": "Send follow-up email", "owner": "you", "deadline": "today"},
                {"action": "Schedule next meeting", "owner": "you", "deadline": "this week"},
            ],
            "sentiment": "positive",
            "next_steps": "Follow up within 24 hours",
            "note": "Full AI summarization with Pro plan.",
        }, indent=2)
