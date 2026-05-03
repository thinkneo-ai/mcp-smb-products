"""ThinkNEO MCP SMB A2A Lite — Agent-to-Agent Protocol for SMEs."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.config import BaseSettings
from shared.server_factory import create_product_mcp
from .tools import register_tools

class Settings(BaseSettings):
    def __init__(self):
        super().__init__(product_name="SMB A2A Lite", default_port=8108)

settings = Settings()
INSTRUCTIONS = (
    "ThinkNEO MCP SMB A2A Lite — Deploy A2A-protocol agents. "
    "Tools:\n"
    "- a2a_register_agent: Register your agent with A2A discovery\n"
    "- a2a_discover_agents: Find agents by capability/skill\n"
    "- a2a_send_task: Send a task to another A2A agent\n"
    "- a2a_get_status: Check task status\n"
    "- a2a_get_agent_card: Get the agent card for any registered agent\n"
    "\nAll tools consume TNC credits."
)
mcp, app = create_product_mcp(settings=settings, instructions=INSTRUCTIONS, register_tools=register_tools, version="1.0.0")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host=settings.host, port=settings.port, workers=1)
