"""ThinkNEO MCP SMB Router — AI Smart Router for SMEs."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.config import BaseSettings
from shared.server_factory import create_product_mcp
from .tools import register_tools

class Settings(BaseSettings):
    def __init__(self):
        super().__init__(product_name="SMB Router", default_port=8104)

settings = Settings()

INSTRUCTIONS = (
    "You are connected to ThinkNEO MCP SMB Router — AI Smart Router. "
    "Routes requests to the best model based on task, quality, and cost. "
    "Tools:\n"
    "- router_route: Find the best model for your task (cheapest that meets quality)\n"
    "- router_compare: Compare models side-by-side for a use case\n"
    "- router_simulate: Simulate savings if you switch to optimal routing\n"
    "- router_providers: List all supported providers and models\n"
    "\nAll tools consume TNC credits."
)

mcp, app = create_product_mcp(
    settings=settings, instructions=INSTRUCTIONS, register_tools=register_tools, version="1.0.0",
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host=settings.host, port=settings.port, workers=1)
