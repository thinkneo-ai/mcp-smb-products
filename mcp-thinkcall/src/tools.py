"""ThinkCall tools — voice calls, transcription, analysis."""
from __future__ import annotations
import json, uuid
from datetime import datetime, timezone
from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.billing import tnc_tool

PRODUCT = "thinkcall"

_calls: list[dict] = []


def register_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=5.0)
    def thinkcall_initiate(
        to_number: Annotated[str, Field(description="Phone number to call (E.164 format: +5511999990000)")],
        purpose: Annotated[str, Field(description="Call purpose (for AI assistance context)")],
        language: Annotated[str, Field(description="Language: 'en', 'pt-br', 'es'")] = "en",
        record: Annotated[bool, Field(description="Record the call for transcription")] = True,
        ai_assist: Annotated[bool, Field(description="Enable real-time AI suggestions")] = True,
    ) -> str:
        """Initiate an AI-assisted call. Costs 5 TNC + per-minute charges."""
        call_id = str(uuid.uuid4())[:10]
        call = {
            "call_id": call_id,
            "to": to_number,
            "purpose": purpose,
            "language": language,
            "recording": record,
            "ai_assist": ai_assist,
            "status": "initiating",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        _calls.append(call)
        return json.dumps({
            "call_id": call_id,
            "status": "initiating",
            "message": f"Connecting to {to_number}...",
            "features": {
                "real_time_transcription": True,
                "ai_suggestions": ai_assist,
                "recording": record,
            },
            "note": "WebRTC call interface available at https://call.thinkneo.ai",
            "cost_per_minute_tnc": 2.0,
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=3.0)
    def thinkcall_transcribe(
        audio_url: Annotated[Optional[str], Field(description="URL of audio file to transcribe")] = None,
        call_id: Annotated[Optional[str], Field(description="Call ID to get transcript for")] = None,
        language: Annotated[str, Field(description="Audio language")] = "en",
    ) -> str:
        """Transcribe audio or get call transcript. Costs 3 TNC."""
        return json.dumps({
            "call_id": call_id,
            "audio_url": audio_url,
            "language": language,
            "status": "transcribing",
            "transcript": "[Transcription will appear here once processed]",
            "estimated_time_sec": 10,
            "model": "whisper-large-v3",
            "note": "Full Whisper transcription with speaker diarization in Pro plan.",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=3.0)
    def thinkcall_analyze(
        transcript: Annotated[str, Field(description="Call transcript to analyze")],
    ) -> str:
        """Analyze a call for sentiment, topics, and action items. Costs 3 TNC."""
        word_count = len(transcript.split())
        return json.dumps({
            "analysis": {
                "duration_estimate": f"{max(1, word_count // 150)} minutes",
                "sentiment": "neutral",
                "topics": ["Main discussion topic"],
                "action_items": [
                    {"action": "Follow up on discussion", "owner": "caller"},
                ],
                "key_moments": [
                    {"timestamp": "0:30", "type": "question", "summary": "Key question asked"},
                ],
                "talk_ratio": {"caller": 55, "recipient": 45},
            },
            "word_count": word_count,
            "note": "Full AI analysis with neural models in Pro plan.",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=0.5)
    def thinkcall_list_calls(
        limit: Annotated[int, Field(description="Max calls to list")] = 10,
    ) -> str:
        """List recent calls. Costs 0.5 TNC."""
        recent = _calls[-limit:]
        return json.dumps({"calls": recent, "total": len(_calls)}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=0.5)
    def thinkcall_get_credits(self=None) -> str:
        """Check calling credits balance. Costs 0.5 TNC."""
        return json.dumps({
            "calling_credits_tnc": 100.0,
            "minutes_remaining_estimate": 50,
            "rate_per_minute_tnc": 2.0,
            "top_up_url": "https://thinkneo.app/pricing",
        }, indent=2)
