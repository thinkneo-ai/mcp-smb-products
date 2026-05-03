"""Memory tools — store, recall, search, manage persistent AI memories."""
from __future__ import annotations
import json, uuid
from datetime import datetime, timezone
from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.billing import tnc_tool

PRODUCT = "memory"

# In-memory store (production: Qdrant/PostgreSQL)
_memories: dict[str, dict] = {}


def register_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def memory_store(
        key: Annotated[str, Field(description="Unique key for this memory")],
        content: Annotated[str, Field(description="Content to remember")],
        tags: Annotated[Optional[str], Field(description="Comma-separated tags")] = None,
        namespace: Annotated[str, Field(description="Namespace (e.g., project name)")] = "default",
        ttl_days: Annotated[Optional[int], Field(description="Auto-delete after N days (null=forever)")] = None,
    ) -> str:
        """Store a memory. Costs 1 TNC."""
        memory_id = str(uuid.uuid4())[:8]
        now = datetime.now(timezone.utc)
        _memories[key] = {
            "id": memory_id,
            "key": key,
            "content": content,
            "tags": [t.strip() for t in (tags or "").split(",") if t.strip()],
            "namespace": namespace,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "ttl_days": ttl_days,
            "access_count": 0,
        }
        return json.dumps({"stored": True, "key": key, "id": memory_id, "namespace": namespace}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def memory_recall(
        query: Annotated[str, Field(description="Key or search term to recall")],
        namespace: Annotated[str, Field(description="Namespace to search in")] = "default",
        limit: Annotated[int, Field(description="Max results")] = 5,
    ) -> str:
        """Recall memories by key or search. Costs 1 TNC."""
        results = []
        query_lower = query.lower()
        for key, mem in _memories.items():
            if mem["namespace"] != namespace and namespace != "all":
                continue
            if query_lower in key.lower() or query_lower in mem["content"].lower() or any(query_lower in t.lower() for t in mem["tags"]):
                mem["access_count"] += 1
                results.append(mem)
        results = results[:limit]
        return json.dumps({"query": query, "results": results, "count": len(results)}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=0.5)
    def memory_list(
        namespace: Annotated[str, Field(description="Namespace filter")] = "default",
        tag: Annotated[Optional[str], Field(description="Filter by tag")] = None,
        limit: Annotated[int, Field(description="Max results")] = 20,
    ) -> str:
        """List stored memories. Costs 0.5 TNC."""
        results = []
        for key, mem in _memories.items():
            if namespace != "all" and mem["namespace"] != namespace:
                continue
            if tag and tag not in mem["tags"]:
                continue
            results.append({"key": key, "tags": mem["tags"], "namespace": mem["namespace"], "created_at": mem["created_at"]})
        return json.dumps({"memories": results[:limit], "total": len(results)}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=0.5)
    def memory_delete(
        key: Annotated[str, Field(description="Key of memory to delete")],
    ) -> str:
        """Delete a specific memory. Costs 0.5 TNC."""
        if key in _memories:
            del _memories[key]
            return json.dumps({"deleted": True, "key": key}, indent=2)
        return json.dumps({"deleted": False, "error": "not_found", "key": key}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=0.5)
    def memory_stats(
        namespace: Annotated[str, Field(description="Namespace")] = "all",
    ) -> str:
        """Get memory usage statistics. Costs 0.5 TNC."""
        mems = list(_memories.values())
        if namespace != "all":
            mems = [m for m in mems if m["namespace"] == namespace]
        total_size = sum(len(m["content"]) for m in mems)
        return json.dumps({
            "total_memories": len(mems),
            "total_size_bytes": total_size,
            "namespaces": list(set(m["namespace"] for m in mems)),
            "most_accessed": sorted(mems, key=lambda x: x["access_count"], reverse=True)[:3],
        }, indent=2)
