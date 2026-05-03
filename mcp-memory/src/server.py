"""ThinkNEO MCP SMB Memory — Persistent AI Agent Memory."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.config import BaseSettings
from shared.server_factory import create_product_mcp
from .tools import register_tools

class Settings(BaseSettings):
    def __init__(self):
        super().__init__(product_name="SMB Memory", default_port=8106)

settings = Settings()
INSTRUCTIONS = (
    "ThinkNEO MCP SMB Memory — Persistent, searchable memory for AI agents. "
    "Tools:\n"
    "- memory_store: Store a memory (key-value with tags and metadata)\n"
    "- memory_recall: Recall memories by key or semantic search\n"
    "- memory_list: List stored memories with filters\n"
    "- memory_delete: Delete a specific memory\n"
    "- memory_stats: Get memory usage stats\n"
    "\nAll tools consume TNC credits."
)
mcp, app = create_product_mcp(settings=settings, instructions=INSTRUCTIONS, register_tools=register_tools, version="1.0.0")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host=settings.host, port=settings.port, workers=1)
