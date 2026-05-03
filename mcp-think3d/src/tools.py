"""Think3D tools — 3D model generation, conversion, management."""
from __future__ import annotations
import json, uuid
from datetime import datetime, timezone
from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.billing import tnc_tool

PRODUCT = "think3d"

_models: dict[str, dict] = {}


def register_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=10.0)
    def think3d_generate(
        prompt: Annotated[str, Field(description="Text description of the 3D model to generate")],
        style: Annotated[str, Field(description="Style: 'realistic', 'cartoon', 'low_poly', 'sculpted'")] = "realistic",
        format: Annotated[str, Field(description="Output format: 'glb', 'obj', 'fbx'")] = "glb",
        with_textures: Annotated[bool, Field(description="Include PBR textures")] = True,
        lod_variants: Annotated[bool, Field(description="Generate LOD variants (high/medium/low)")] = False,
    ) -> str:
        """Generate a 3D model from text description. Costs 10 TNC."""
        model_id = str(uuid.uuid4())[:10]
        model = {
            "model_id": model_id,
            "prompt": prompt,
            "style": style,
            "format": format,
            "with_textures": with_textures,
            "lod_variants": lod_variants,
            "status": "processing",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "estimated_time_sec": 30,
        }
        _models[model_id] = model
        return json.dumps({
            "model_id": model_id,
            "status": "processing",
            "estimated_time_sec": 30,
            "message": f"Generating 3D model: '{prompt}' in {style} style ({format} format)",
            "check_status": f"Use think3d_get_model with model_id='{model_id}'",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=12.0)
    def think3d_from_image(
        image_url: Annotated[str, Field(description="URL of the image to convert to 3D")],
        format: Annotated[str, Field(description="Output format: 'glb', 'obj', 'fbx'")] = "glb",
        with_textures: Annotated[bool, Field(description="Include PBR textures")] = True,
    ) -> str:
        """Generate 3D model from an image. Costs 12 TNC."""
        model_id = str(uuid.uuid4())[:10]
        model = {
            "model_id": model_id,
            "source": "image",
            "image_url": image_url,
            "format": format,
            "status": "processing",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        _models[model_id] = model
        return json.dumps({
            "model_id": model_id,
            "status": "processing",
            "estimated_time_sec": 45,
            "message": "Processing image to 3D conversion...",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def think3d_list_models(
        limit: Annotated[int, Field(description="Max models to list")] = 10,
    ) -> str:
        """List your generated 3D models. Costs 1 TNC."""
        models = list(_models.values())[-limit:]
        summaries = [{"model_id": m["model_id"], "prompt": m.get("prompt", "image-to-3d"), "status": m["status"], "format": m.get("format", "glb"), "created_at": m["created_at"]} for m in models]
        return json.dumps({"models": summaries, "total": len(_models)}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def think3d_get_model(
        model_id: Annotated[str, Field(description="Model ID to retrieve")],
    ) -> str:
        """Get model details and download URL. Costs 1 TNC."""
        if model_id not in _models:
            return json.dumps({"error": "model_not_found", "model_id": model_id}, indent=2)
        model = _models[model_id]
        # Simulate completion
        model["status"] = "completed"
        model["download_url"] = f"https://cdn.thinkneo.app/3d/{model_id}.{model.get('format', 'glb')}"
        model["file_size_mb"] = 4.2
        return json.dumps(model, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=5.0)
    def think3d_convert(
        model_id: Annotated[str, Field(description="Model ID to convert")],
        target_format: Annotated[str, Field(description="Target format: 'glb', 'obj', 'fbx', 'stl', 'usdz'")],
    ) -> str:
        """Convert a 3D model to another format. Costs 5 TNC."""
        if model_id not in _models:
            return json.dumps({"error": "model_not_found"}, indent=2)
        return json.dumps({
            "model_id": model_id,
            "original_format": _models[model_id].get("format", "glb"),
            "target_format": target_format,
            "status": "converting",
            "download_url": f"https://cdn.thinkneo.app/3d/{model_id}.{target_format}",
            "estimated_time_sec": 15,
        }, indent=2)
