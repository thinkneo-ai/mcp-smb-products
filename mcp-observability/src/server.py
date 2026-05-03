"""ThinkNEO MCP SMB Observability — Trace visibility for AI agents."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.config import BaseSettings
from shared.server_factory import create_product_mcp
from .tools import register_tools

class Settings(BaseSettings):
    def __init__(self):
        super().__init__(product_name="SMB Observability", default_port=8103)

settings = Settings()

INSTRUCTIONS = (
    "You are connected to ThinkNEO MCP SMB Observability — trace visibility for AI agents. "
    "Tools:\n"
    "- obs_start_trace: Begin a new trace/session for an AI agent operation\n"
    "- obs_log_event: Log an event within an active trace (LLM call, tool use, decision)\n"
    "- obs_end_trace: End a trace and get summary (duration, cost, events)\n"
    "- obs_get_dashboard: Get aggregated metrics (latency, errors, costs)\n"
    "- obs_list_traces: List recent traces with filters\n"
    "\nAll tools consume TNC credits. Get credits at https://thinkneo.app/pricing"
)

mcp, app = create_product_mcp(
    settings=settings, instructions=INSTRUCTIONS, register_tools=register_tools, version="1.0.0",
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host=settings.host, port=settings.port, workers=1)
