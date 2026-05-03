"""ThinkNEO MCP SMB Trust Score — AI Governance Scoring."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.config import BaseSettings
from shared.server_factory import create_product_mcp
from .tools import register_tools

class Settings(BaseSettings):
    def __init__(self):
        super().__init__(product_name="SMB Trust Score", default_port=8105)

settings = Settings()
INSTRUCTIONS = (
    "ThinkNEO MCP SMB Trust Score — AI Governance Scoring (0-100). "
    "Tools:\n"
    "- trust_evaluate: Evaluate your AI governance posture (10 categories)\n"
    "- trust_get_badge: Get your trust badge (Platinum/Gold/Silver/Bronze)\n"
    "- trust_recommendations: Get actionable recommendations to improve score\n"
    "- trust_history: View score history over time\n"
    "\nAll tools consume TNC credits."
)
mcp, app = create_product_mcp(settings=settings, instructions=INSTRUCTIONS, register_tools=register_tools, version="1.0.0")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host=settings.host, port=settings.port, workers=1)
