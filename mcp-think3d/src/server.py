"""ThinkNEO MCP SMB Think3D — 3D Model Generation."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.config import BaseSettings
from shared.server_factory import create_product_mcp
from .tools import register_tools

class Settings(BaseSettings):
    def __init__(self):
        super().__init__(product_name="SMB Think3D", default_port=8111)

settings = Settings()
INSTRUCTIONS = (
    "ThinkNEO MCP SMB Think3D — Generate 3D models from text or images. "
    "Tools:\n"
    "- think3d_generate: Generate a 3D model from text description\n"
    "- think3d_from_image: Generate 3D model from an image URL\n"
    "- think3d_list_models: List your generated 3D models\n"
    "- think3d_get_model: Get download URL for a generated model\n"
    "- think3d_convert: Convert between 3D formats (GLB/OBJ/FBX)\n"
    "\nAll tools consume TNC credits."
)
mcp, app = create_product_mcp(settings=settings, instructions=INSTRUCTIONS, register_tools=register_tools, version="1.0.0")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.server:app", host=settings.host, port=settings.port, workers=1)
