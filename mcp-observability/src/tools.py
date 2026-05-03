"""Observability tools — tracing, events, dashboard for AI agents."""
from __future__ import annotations
import json, uuid
from datetime import datetime, timezone
from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.billing import tnc_tool

PRODUCT = "observability"

# In-memory trace store (production would use DB)
_traces: dict[str, dict] = {}


def register_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def obs_start_trace(
        agent_name: Annotated[str, Field(description="Name of the AI agent being traced")],
        operation: Annotated[str, Field(description="Operation being performed (e.g., 'customer_support_ticket')")],
        metadata: Annotated[Optional[str], Field(description="JSON metadata string")] = None,
    ) -> str:
        """Start a new trace for an AI agent operation. Costs 1 TNC."""
        trace_id = str(uuid.uuid4())[:12]
        now = datetime.now(timezone.utc)
        trace = {
            "trace_id": trace_id,
            "agent_name": agent_name,
            "operation": operation,
            "started_at": now.isoformat(),
            "events": [],
            "status": "active",
            "metadata": json.loads(metadata) if metadata else {},
        }
        _traces[trace_id] = trace
        return json.dumps({"trace_id": trace_id, "status": "active", "started_at": now.isoformat()}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=0.5)
    def obs_log_event(
        trace_id: Annotated[str, Field(description="Trace ID to log event to")],
        event_type: Annotated[str, Field(description="Event type: 'llm_call', 'tool_use', 'decision', 'error', 'custom'")],
        description: Annotated[str, Field(description="What happened")],
        duration_ms: Annotated[Optional[int], Field(description="Duration in milliseconds")] = None,
        cost_usd: Annotated[Optional[float], Field(description="Cost in USD")] = None,
        model: Annotated[Optional[str], Field(description="Model used (if LLM call)")] = None,
    ) -> str:
        """Log an event within a trace. Costs 0.5 TNC."""
        if trace_id not in _traces:
            return json.dumps({"error": "trace_not_found", "trace_id": trace_id}, indent=2)
        event = {
            "event_id": str(uuid.uuid4())[:8],
            "type": event_type,
            "description": description,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration_ms,
            "cost_usd": cost_usd,
            "model": model,
        }
        _traces[trace_id]["events"].append(event)
        return json.dumps({"logged": True, "event_id": event["event_id"], "trace_events_count": len(_traces[trace_id]["events"])}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def obs_end_trace(
        trace_id: Annotated[str, Field(description="Trace ID to end")],
        outcome: Annotated[str, Field(description="Outcome: 'success', 'failure', 'partial'")] = "success",
    ) -> str:
        """End a trace and get summary. Costs 1 TNC."""
        if trace_id not in _traces:
            return json.dumps({"error": "trace_not_found", "trace_id": trace_id}, indent=2)
        trace = _traces[trace_id]
        trace["status"] = "completed"
        trace["outcome"] = outcome
        trace["ended_at"] = datetime.now(timezone.utc).isoformat()
        total_duration = sum(e.get("duration_ms", 0) or 0 for e in trace["events"])
        total_cost = sum(e.get("cost_usd", 0) or 0 for e in trace["events"])
        return json.dumps({
            "trace_id": trace_id,
            "status": "completed",
            "outcome": outcome,
            "total_events": len(trace["events"]),
            "total_duration_ms": total_duration,
            "total_cost_usd": round(total_cost, 6),
            "started_at": trace["started_at"],
            "ended_at": trace["ended_at"],
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=2.0)
    def obs_get_dashboard(
        period: Annotated[str, Field(description="Period: 'hour', 'day', 'week'")] = "day",
    ) -> str:
        """Get aggregated observability dashboard. Costs 2 TNC."""
        active = sum(1 for t in _traces.values() if t["status"] == "active")
        completed = sum(1 for t in _traces.values() if t["status"] == "completed")
        all_events = [e for t in _traces.values() for e in t["events"]]
        return json.dumps({
            "period": period,
            "traces": {"active": active, "completed": completed, "total": len(_traces)},
            "events_total": len(all_events),
            "avg_duration_ms": sum(e.get("duration_ms", 0) or 0 for e in all_events) / max(len(all_events), 1),
            "total_cost_usd": round(sum(e.get("cost_usd", 0) or 0 for e in all_events), 4),
            "error_rate_pct": round(sum(1 for e in all_events if e["type"] == "error") / max(len(all_events), 1) * 100, 1),
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def obs_list_traces(
        status: Annotated[Optional[str], Field(description="Filter by status: 'active', 'completed'")] = None,
        limit: Annotated[int, Field(description="Max traces to return")] = 10,
    ) -> str:
        """List recent traces. Costs 1 TNC."""
        traces = list(_traces.values())
        if status:
            traces = [t for t in traces if t["status"] == status]
        traces = traces[-limit:]
        summaries = [{
            "trace_id": t["trace_id"], "agent": t["agent_name"], "operation": t["operation"],
            "status": t["status"], "events": len(t["events"]), "started_at": t["started_at"],
        } for t in traces]
        return json.dumps({"traces": summaries, "total": len(summaries)}, indent=2)
