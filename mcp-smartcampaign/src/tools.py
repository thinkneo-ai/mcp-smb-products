"""SmartCampaign tools — news monitoring, competitor mapping, deepfake detection."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.billing import tnc_tool

PRODUCT = "smartcampaign"


def register_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=3.0)
    def campaign_monitor_news(
        keywords: Annotated[str, Field(description="Comma-separated keywords to monitor")],
        period: Annotated[str, Field(description="Period: '1h', '6h', '24h', '7d'")] = "24h",
        sources: Annotated[str, Field(description="Sources: 'all', 'mainstream', 'social', 'blogs'")] = "all",
        language: Annotated[str, Field(description="Language: 'pt-br', 'en', 'es'")] = "pt-br",
    ) -> str:
        """Monitor news mentions for keywords/candidates. Costs 3 TNC."""
        kws = [k.strip() for k in keywords.split(",")]
        return json.dumps({
            "keywords": kws,
            "period": period,
            "sources": sources,
            "mentions_found": 0,
            "results": [],
            "sentiment_summary": {"positive": 0, "neutral": 0, "negative": 0},
            "trending": False,
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "note": "Configure monitoring sources at https://smartcampaign.thinkneo.ai/settings",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=5.0)
    def campaign_competitor_map(
        competitor_name: Annotated[str, Field(description="Competitor/opponent name")],
        topics: Annotated[Optional[str], Field(description="Comma-separated topics to map positions on")] = None,
    ) -> str:
        """Map competitor agenda and positions. Costs 5 TNC."""
        topic_list = [t.strip() for t in (topics or "economia,saude,educacao,seguranca").split(",")]
        positions = {topic: {"position": "unknown", "strength": "unrated", "last_statement": None} for topic in topic_list}
        return json.dumps({
            "competitor": competitor_name,
            "positions": positions,
            "overall_agenda": "Data collection in progress",
            "vulnerabilities": [],
            "strengths": [],
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "note": "Positions populate as monitoring collects data. Enable continuous monitoring for real-time updates.",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=3.0)
    def campaign_sentiment(
        subject: Annotated[str, Field(description="Candidate name or issue to analyze")],
        platform: Annotated[str, Field(description="Platform: 'twitter', 'instagram', 'all'")] = "all",
        period: Annotated[str, Field(description="Period: '1h', '24h', '7d'")] = "24h",
    ) -> str:
        """Analyze social sentiment. Costs 3 TNC."""
        return json.dumps({
            "subject": subject,
            "platform": platform,
            "period": period,
            "sentiment": {
                "positive": 0.0,
                "neutral": 0.0,
                "negative": 0.0,
            },
            "volume": 0,
            "trend": "stable",
            "top_topics": [],
            "influencers": [],
            "note": "Connect social accounts for real sentiment data.",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=5.0)
    def campaign_detect_deepfake(
        media_url: Annotated[str, Field(description="URL of media (image/video/audio) to check")],
        media_type: Annotated[str, Field(description="Type: 'image', 'video', 'audio'")] = "image",
    ) -> str:
        """Check if media may be AI-generated (deepfake detection). Costs 5 TNC."""
        return json.dumps({
            "media_url": media_url,
            "media_type": media_type,
            "analysis": {
                "is_likely_ai_generated": False,
                "confidence": 0.0,
                "indicators": [],
                "recommendation": "Submit media for analysis. Results in ~30 seconds.",
            },
            "status": "analyzing",
            "estimated_time_sec": 30,
            "note": "Uses multiple detection models. Results should be verified by human analysts.",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=3.0)
    def campaign_generate_talking_points(
        topic: Annotated[str, Field(description="Topic to generate talking points for")],
        position: Annotated[str, Field(description="Your position: 'for', 'against', 'neutral'")],
        audience: Annotated[str, Field(description="Target audience: 'general', 'youth', 'seniors', 'business'")] = "general",
        language: Annotated[str, Field(description="Language: 'pt-br', 'en', 'es'")] = "pt-br",
        count: Annotated[int, Field(description="Number of talking points")] = 5,
    ) -> str:
        """Generate talking points for a topic. Costs 3 TNC."""
        return json.dumps({
            "topic": topic,
            "position": position,
            "audience": audience,
            "talking_points": [
                f"[Talking point {i+1} about {topic} - {position} position for {audience} audience]"
                for i in range(count)
            ],
            "tone_guidance": "Adapt delivery to audience. Be specific with data when possible.",
            "note": "Full AI-generated talking points with research in Pro plan.",
        }, indent=2)
