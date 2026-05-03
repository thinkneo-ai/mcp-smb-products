"""ThinkNEO MCP SMB SmartCampaign — Political Campaign Intelligence."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.config import BaseSettings
from shared.server_factory import create_product_mcp
from .tools import register_tools

class Settings(BaseSettings):
    def __init__(self):
        super().__init__(product_name="SMB SmartCampaign", default_port=8113)

settings = Settings()
INSTRUCTIONS = (
    "ThinkNEO MCP SMB SmartCampaign — Campaign Intelligence Platform. "
    "Tools:\n"
    "- campaign_monitor_news: Monitor news mentions for a candidate/topic\n"
    "- campaign_competitor_map: Map competitor agenda and positions\n"
    "- campaign_sentiment: Analyze social sentiment for a candidate/issue\n"
    "- campaign_detect_deepfake: Check if media content may be AI-generated\n"
    "- campaign_generate_talking_points: Generate talking points for a topic\n"
    "\nAll tools consume TNC credits."
)
mcp, app = create_product_mcp(settings=settings, instructions=INSTRUCTIONS, register_tools=register_tools, version="1.0.0")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host=settings.host, port=settings.port, workers=1)
