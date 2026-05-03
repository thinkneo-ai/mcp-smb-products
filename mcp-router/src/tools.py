"""Router tools — model selection, comparison, savings simulation."""
from __future__ import annotations
import json
from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.billing import tnc_tool

PRODUCT = "router"

MODELS = {
    "claude-opus-4": {"provider": "Anthropic", "input": 15.0, "output": 75.0, "context": 200000, "quality": 98, "speed": "slow"},
    "claude-sonnet-4": {"provider": "Anthropic", "input": 3.0, "output": 15.0, "context": 200000, "quality": 92, "speed": "fast"},
    "claude-haiku-4": {"provider": "Anthropic", "input": 0.80, "output": 4.0, "context": 200000, "quality": 82, "speed": "very_fast"},
    "gpt-4o": {"provider": "OpenAI", "input": 2.50, "output": 10.0, "context": 128000, "quality": 90, "speed": "fast"},
    "gpt-4o-mini": {"provider": "OpenAI", "input": 0.15, "output": 0.60, "context": 128000, "quality": 78, "speed": "very_fast"},
    "gpt-4.1": {"provider": "OpenAI", "input": 2.0, "output": 8.0, "context": 1000000, "quality": 93, "speed": "fast"},
    "gemini-2.5-pro": {"provider": "Google", "input": 1.25, "output": 10.0, "context": 1000000, "quality": 91, "speed": "fast"},
    "gemini-2.5-flash": {"provider": "Google", "input": 0.15, "output": 0.60, "context": 1000000, "quality": 80, "speed": "very_fast"},
    "mistral-large": {"provider": "Mistral", "input": 2.0, "output": 6.0, "context": 128000, "quality": 85, "speed": "fast"},
    "mistral-small": {"provider": "Mistral", "input": 0.10, "output": 0.30, "context": 128000, "quality": 72, "speed": "very_fast"},
    "llama-4-maverick": {"provider": "Meta", "input": 0.20, "output": 0.60, "context": 1000000, "quality": 84, "speed": "fast"},
    "llama-4-scout": {"provider": "Meta", "input": 0.10, "output": 0.30, "context": 500000, "quality": 76, "speed": "very_fast"},
    "deepseek-v3": {"provider": "DeepSeek", "input": 0.14, "output": 0.28, "context": 128000, "quality": 82, "speed": "fast"},
    "deepseek-r1": {"provider": "DeepSeek", "input": 0.55, "output": 2.19, "context": 128000, "quality": 90, "speed": "slow"},
    "qwen-3-235b": {"provider": "Alibaba", "input": 0.80, "output": 2.40, "context": 128000, "quality": 86, "speed": "fast"},
    "command-r-plus": {"provider": "Cohere", "input": 2.50, "output": 10.0, "context": 128000, "quality": 82, "speed": "fast"},
    "grok-3": {"provider": "xAI", "input": 3.0, "output": 15.0, "context": 131072, "quality": 89, "speed": "fast"},
}

USE_CASE_QUALITY = {
    "coding": 85, "summarization": 70, "translation": 75, "analysis": 80,
    "creative_writing": 85, "data_extraction": 70, "classification": 65,
    "conversation": 75, "reasoning": 90, "math": 88,
}


def register_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=2.0)
    def router_route(
        task: Annotated[str, Field(description="Task type: coding, summarization, translation, analysis, creative_writing, data_extraction, classification, conversation, reasoning, math")],
        min_quality: Annotated[Optional[int], Field(description="Minimum quality score (0-100)")] = None,
        max_cost_per_1m: Annotated[Optional[float], Field(description="Max USD per 1M output tokens")] = None,
        prefer_speed: Annotated[bool, Field(description="Prefer faster models")] = False,
    ) -> str:
        """Find the best model for your task. Costs 2 TNC."""
        threshold = min_quality or USE_CASE_QUALITY.get(task, 75)
        candidates = []
        for name, info in MODELS.items():
            if info["quality"] >= threshold:
                if max_cost_per_1m and info["output"] > max_cost_per_1m:
                    continue
                candidates.append({"model": name, **info})
        if prefer_speed:
            candidates.sort(key=lambda x: (0 if x["speed"] == "very_fast" else 1 if x["speed"] == "fast" else 2, x["output"]))
        else:
            candidates.sort(key=lambda x: x["output"])
        return json.dumps({
            "task": task,
            "min_quality": threshold,
            "recommended": candidates[0]["model"] if candidates else None,
            "alternatives": [c["model"] for c in candidates[1:4]],
            "details": candidates[:5],
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def router_compare(
        models: Annotated[str, Field(description="Comma-separated model names to compare")],
    ) -> str:
        """Compare models side-by-side. Costs 1 TNC."""
        names = [m.strip() for m in models.split(",")]
        results = []
        for name in names:
            if name in MODELS:
                results.append({"model": name, **MODELS[name]})
            else:
                results.append({"model": name, "error": "not_found"})
        return json.dumps({"comparison": results, "models_compared": len(results)}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=2.0)
    def router_simulate(
        current_model: Annotated[str, Field(description="Model you currently use")],
        monthly_tokens: Annotated[int, Field(description="Estimated monthly tokens (input+output)")] = 1000000,
        task: Annotated[str, Field(description="Primary task type")] = "conversation",
    ) -> str:
        """Simulate savings if you switch to optimal routing. Costs 2 TNC."""
        current = MODELS.get(current_model)
        if not current:
            return json.dumps({"error": "model_not_found", "model": current_model}, indent=2)
        threshold = USE_CASE_QUALITY.get(task, 75)
        cheapest = min((m for m in MODELS.values() if m["quality"] >= threshold), key=lambda x: x["output"], default=None)
        current_cost = monthly_tokens / 1_000_000 * (current["input"] * 0.7 + current["output"] * 0.3)
        optimal_cost = monthly_tokens / 1_000_000 * (cheapest["input"] * 0.7 + cheapest["output"] * 0.3) if cheapest else current_cost
        return json.dumps({
            "current_model": current_model,
            "current_monthly_cost_usd": round(current_cost, 2),
            "optimal_monthly_cost_usd": round(optimal_cost, 2),
            "monthly_savings_usd": round(current_cost - optimal_cost, 2),
            "annual_savings_usd": round((current_cost - optimal_cost) * 12, 2),
            "savings_pct": round((1 - optimal_cost / current_cost) * 100, 1) if current_cost > 0 else 0,
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=0.5)
    def router_providers(self=None) -> str:
        """List all supported providers and models. Costs 0.5 TNC."""
        providers = {}
        for model, info in MODELS.items():
            p = info["provider"]
            if p not in providers:
                providers[p] = []
            providers[p].append({"model": model, "quality": info["quality"], "output_cost_per_1m": info["output"]})
        return json.dumps({"providers": providers, "total_models": len(MODELS)}, indent=2)
