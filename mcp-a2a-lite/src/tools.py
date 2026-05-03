"""A2A Lite tools — agent registration, discovery, task dispatch."""
from __future__ import annotations
import json, uuid
from datetime import datetime, timezone
from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.billing import tnc_tool

PRODUCT = "a2a-lite"

_agents: dict[str, dict] = {}
_tasks: dict[str, dict] = {}


def register_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=5.0)
    def a2a_register_agent(
        name: Annotated[str, Field(description="Agent name")],
        description: Annotated[str, Field(description="What this agent does")],
        skills: Annotated[str, Field(description="Comma-separated skills (e.g., 'translation,summarization')")],
        endpoint_url: Annotated[str, Field(description="Your agent's A2A endpoint URL")],
        auth_type: Annotated[str, Field(description="Auth type: 'bearer', 'none', 'oauth2'")] = "bearer",
    ) -> str:
        """Register your agent for A2A discovery. Costs 5 TNC."""
        agent_id = str(uuid.uuid4())[:8]
        agent = {
            "agent_id": agent_id,
            "name": name,
            "description": description,
            "skills": [s.strip() for s in skills.split(",")],
            "endpoint_url": endpoint_url,
            "auth_type": auth_type,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "protocol_version": "0.3",
        }
        _agents[agent_id] = agent
        return json.dumps({
            "registered": True,
            "agent_id": agent_id,
            "discovery_url": f"https://mcp.thinkneo.app/a2a-lite/.well-known/agent-card/{agent_id}.json",
            "agent_card": agent,
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def a2a_discover_agents(
        skill: Annotated[Optional[str], Field(description="Skill to search for")] = None,
        query: Annotated[Optional[str], Field(description="Free-text search")] = None,
        limit: Annotated[int, Field(description="Max results")] = 10,
    ) -> str:
        """Discover A2A agents by skill or keyword. Costs 1 TNC."""
        results = list(_agents.values())
        if skill:
            results = [a for a in results if skill.lower() in [s.lower() for s in a["skills"]]]
        if query:
            q = query.lower()
            results = [a for a in results if q in a["name"].lower() or q in a["description"].lower()]
        results = results[:limit]
        return json.dumps({"agents": results, "count": len(results)}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=3.0)
    def a2a_send_task(
        target_agent_id: Annotated[str, Field(description="Target agent ID")],
        task_description: Annotated[str, Field(description="Task to send to the agent")],
        input_data: Annotated[Optional[str], Field(description="JSON input data for the task")] = None,
    ) -> str:
        """Send a task to an A2A agent. Costs 3 TNC."""
        if target_agent_id not in _agents:
            return json.dumps({"error": "agent_not_found", "agent_id": target_agent_id}, indent=2)
        task_id = str(uuid.uuid4())[:10]
        task = {
            "task_id": task_id,
            "target_agent": target_agent_id,
            "description": task_description,
            "input": json.loads(input_data) if input_data else None,
            "status": "submitted",
            "submitted_at": datetime.now(timezone.utc).isoformat(),
        }
        _tasks[task_id] = task
        return json.dumps({"task_id": task_id, "status": "submitted", "target_agent": _agents[target_agent_id]["name"]}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=0.5)
    def a2a_get_status(
        task_id: Annotated[str, Field(description="Task ID to check")],
    ) -> str:
        """Check A2A task status. Costs 0.5 TNC."""
        if task_id not in _tasks:
            return json.dumps({"error": "task_not_found", "task_id": task_id}, indent=2)
        return json.dumps(_tasks[task_id], indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=0.5)
    def a2a_get_agent_card(
        agent_id: Annotated[str, Field(description="Agent ID")],
    ) -> str:
        """Get agent card (A2A protocol discovery format). Costs 0.5 TNC."""
        if agent_id not in _agents:
            return json.dumps({"error": "agent_not_found"}, indent=2)
        agent = _agents[agent_id]
        card = {
            "name": agent["name"],
            "description": agent["description"],
            "url": agent["endpoint_url"],
            "version": agent["protocol_version"],
            "capabilities": {"streaming": False, "pushNotifications": False},
            "skills": [{"id": s, "name": s} for s in agent["skills"]],
            "authentication": {"schemes": [agent["auth_type"]]},
        }
        return json.dumps(card, indent=2)
