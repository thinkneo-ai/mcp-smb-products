"""ThinkNEO MCP SMB ThinkSecure — Runtime AI Security Controls."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.config import BaseSettings
from shared.server_factory import create_product_mcp
from .tools import register_tools

class Settings(BaseSettings):
    def __init__(self):
        super().__init__(product_name="SMB ThinkSecure", default_port=8107)

settings = Settings()
INSTRUCTIONS = (
    "ThinkNEO MCP SMB ThinkSecure — Runtime security for AI workloads. "
    "Tools:\n"
    "- secure_sanitize_input: Sanitize user input before sending to AI\n"
    "- secure_validate_output: Validate AI output for safety before returning to user\n"
    "- secure_audit_log: Log AI interaction for SOC2/GDPR compliance\n"
    "- secure_check_permissions: Verify user has permission for the AI action\n"
    "- secure_export_audit: Export audit log in compliance format (CSV/JSON)\n"
    "\nAll tools consume TNC credits."
)
mcp, app = create_product_mcp(settings=settings, instructions=INSTRUCTIONS, register_tools=register_tools, version="1.0.0")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host=settings.host, port=settings.port, workers=1)
