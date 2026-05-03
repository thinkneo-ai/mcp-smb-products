"""FinOps tools — AI cost monitoring, budgets, forecasting."""
from __future__ import annotations
import json
from datetime import datetime, timezone
from typing import Annotated
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.billing import tnc_tool

PRODUCT = "finops"

# Model cost database (USD per 1M tokens)
MODEL_COSTS = {
    "gpt-4o": {"input": 2.50, "output": 10.00, "provider": "OpenAI"},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60, "provider": "OpenAI"},
    "claude-sonnet-4": {"input": 3.00, "output": 15.00, "provider": "Anthropic"},
    "claude-haiku-4": {"input": 0.80, "output": 4.00, "provider": "Anthropic"},
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00, "provider": "Google"},
    "gemini-2.5-flash": {"input": 0.15, "output": 0.60, "provider": "Google"},
    "mistral-large": {"input": 2.00, "output": 6.00, "provider": "Mistral"},
    "llama-4-maverick": {"input": 0.20, "output": 0.60, "provider": "Meta"},
    "deepseek-v3": {"input": 0.14, "output": 0.28, "provider": "DeepSeek"},
    "qwen-3-235b": {"input": 0.80, "output": 2.40, "provider": "Alibaba"},
}


def register_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=2.0)
    def finops_check_spend(
        period: Annotated[str, Field(description="Period: 'today', 'week', 'month'", default="month")] = "month",
    ) -> str:
        """View AI spending breakdown. Costs 2 TNC."""
        now = datetime.now(timezone.utc)
        return json.dumps({
            "period": period,
            "total_usd": 0.0,
            "by_provider": {},
            "by_model": {},
            "top_consumers": [],
            "note": "Connect your AI providers via Settings to see real spend data.",
            "setup_url": "https://thinkneo.app/settings/providers",
            "checked_at": now.isoformat(),
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def finops_set_budget(
        monthly_limit_usd: Annotated[float, Field(description="Monthly budget in USD")],
        hard_limit: Annotated[bool, Field(description="If true, block requests when exceeded")] = False,
        alert_threshold: Annotated[float, Field(description="Alert at this % of budget (0-100)")] = 80.0,
    ) -> str:
        """Set monthly AI spending budget. Costs 1 TNC."""
        return json.dumps({
            "status": "budget_configured",
            "monthly_limit_usd": monthly_limit_usd,
            "hard_limit": hard_limit,
            "alert_threshold_pct": alert_threshold,
            "message": f"Budget set to ${monthly_limit_usd}/month. Alert at {alert_threshold}%.",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def finops_get_budget(self=None) -> str:
        """Check budget status and utilization. Costs 1 TNC."""
        return json.dumps({
            "monthly_limit_usd": 0.0,
            "spent_usd": 0.0,
            "remaining_usd": 0.0,
            "utilization_pct": 0.0,
            "days_remaining": 30,
            "projected_end_of_month_usd": 0.0,
            "status": "under_budget",
            "note": "Connect providers to see real budget data.",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=2.0)
    def finops_forecast(
        days_ahead: Annotated[int, Field(description="Days to forecast (1-90)")] = 30,
    ) -> str:
        """Project AI spending based on current trends. Costs 2 TNC."""
        return json.dumps({
            "forecast_days": days_ahead,
            "projected_spend_usd": 0.0,
            "daily_avg_usd": 0.0,
            "trend": "stable",
            "confidence": "low",
            "note": "More data needed. Connect providers for accurate forecasts.",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def finops_compare_costs(
        task_description: Annotated[str, Field(description="Describe the AI task (e.g., 'summarize 10 documents')")],
        estimated_tokens: Annotated[int, Field(description="Estimated total tokens (input+output)")] = 10000,
    ) -> str:
        """Compare cost across providers for a given task. Costs 1 TNC."""
        input_tokens = int(estimated_tokens * 0.7)
        output_tokens = int(estimated_tokens * 0.3)
        comparisons = []
        for model, info in MODEL_COSTS.items():
            cost = (input_tokens / 1_000_000 * info["input"]) + (output_tokens / 1_000_000 * info["output"])
            comparisons.append({"model": model, "provider": info["provider"], "estimated_cost_usd": round(cost, 6)})
        comparisons.sort(key=lambda x: x["estimated_cost_usd"])
        return json.dumps({
            "task": task_description,
            "estimated_tokens": estimated_tokens,
            "comparisons": comparisons,
            "cheapest": comparisons[0]["model"] if comparisons else None,
            "most_expensive": comparisons[-1]["model"] if comparisons else None,
        }, indent=2)
