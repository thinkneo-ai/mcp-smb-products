"""ThinkNEO MCP SMB ThinkCall — AI Voice Calling Platform."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.config import BaseSettings
from shared.server_factory import create_product_mcp
from .tools import register_tools

class Settings(BaseSettings):
    def __init__(self):
        super().__init__(product_name="SMB ThinkCall", default_port=8112)

settings = Settings()
INSTRUCTIONS = (
    "ThinkNEO MCP SMB ThinkCall — AI-powered voice calling. "
    "Tools:\n"
    "- thinkcall_initiate: Start an AI-assisted call\n"
    "- thinkcall_transcribe: Transcribe audio/call recording\n"
    "- thinkcall_analyze: Analyze a call (sentiment, topics, action items)\n"
    "- thinkcall_list_calls: List recent calls\n"
    "- thinkcall_get_credits: Check calling credits balance\n"
    "\nAll tools consume TNC credits."
)
mcp, app = create_product_mcp(settings=settings, instructions=INSTRUCTIONS, register_tools=register_tools, version="1.0.0")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host=settings.host, port=settings.port, workers=1)
