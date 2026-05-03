"""ThinkNEO MCP SMB FinOps — AI Cost Management for SMEs."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.config import BaseSettings
from shared.server_factory import create_product_mcp
from .tools import register_tools

class Settings(BaseSettings):
    def __init__(self):
        super().__init__(product_name="SMB FinOps", default_port=8102)

settings = Settings()

INSTRUCTIONS = (
    "You are connected to ThinkNEO MCP SMB FinOps — AI cost management for SMEs. "
    "Tools:\n"
    "- finops_check_spend: View AI spending breakdown by provider/model/team\n"
    "- finops_set_budget: Set monthly budget with hard/soft limits\n"
    "- finops_get_budget: Check budget status and utilization\n"
    "- finops_forecast: Project spending for the rest of the month\n"
    "- finops_compare_costs: Compare cost across providers for a task\n"
    "\nAll tools consume TNC credits. Get credits at https://thinkneo.app/pricing"
)

mcp, app = create_product_mcp(
    settings=settings, instructions=INSTRUCTIONS, register_tools=register_tools, version="1.0.0",
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host=settings.host, port=settings.port, workers=1)
