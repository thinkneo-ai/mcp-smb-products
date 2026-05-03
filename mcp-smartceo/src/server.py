"""ThinkNEO MCP SMB SmartCEO — Live Call AI Briefing for SMEs."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.config import BaseSettings
from shared.server_factory import create_product_mcp
from .tools import register_tools

class Settings(BaseSettings):
    def __init__(self):
        super().__init__(product_name="SMB SmartCEO", default_port=8109)

settings = Settings()
INSTRUCTIONS = (
    "ThinkNEO MCP SMB SmartCEO — AI briefing for live calls. "
    "Tools:\n"
    "- smartceo_brief: Generate real-time briefing for a contact/company before a call\n"
    "- smartceo_translate: Real-time translation (EN/PT-BR/ES)\n"
    "- smartceo_detect_intent: Detect caller intent from transcript\n"
    "- smartceo_suggest_response: AI response suggestions during call\n"
    "- smartceo_summarize_call: Post-call summary with action items\n"
    "\nAll tools consume TNC credits."
)
mcp, app = create_product_mcp(settings=settings, instructions=INSTRUCTIONS, register_tools=register_tools, version="1.0.0")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host=settings.host, port=settings.port, workers=1)
