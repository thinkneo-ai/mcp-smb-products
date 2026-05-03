"""ThinkNEO MCP SMB Mary — AI Executive Assistant."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.config import BaseSettings
from shared.server_factory import create_product_mcp
from .tools import register_tools

class Settings(BaseSettings):
    def __init__(self):
        super().__init__(product_name="SMB Mary", default_port=8110)

settings = Settings()
INSTRUCTIONS = (
    "ThinkNEO MCP SMB Mary — Your AI Executive Assistant. "
    "Tools:\n"
    "- mary_manage_task: Create, update, or list tasks\n"
    "- mary_manage_contacts: Search, add, or update contacts\n"
    "- mary_schedule: Schedule meetings and reminders\n"
    "- mary_summarize_doc: Summarize a document or email\n"
    "- mary_draft_email: Draft professional emails\n"
    "- mary_expense_track: Track expenses and budgets\n"
    "\nAll tools consume TNC credits."
)
mcp, app = create_product_mcp(settings=settings, instructions=INSTRUCTIONS, register_tools=register_tools, version="1.0.0")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host=settings.host, port=settings.port, workers=1)
