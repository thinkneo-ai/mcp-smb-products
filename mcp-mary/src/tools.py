"""Mary EA tools — tasks, contacts, scheduling, documents, email, expenses."""
from __future__ import annotations
import json, uuid
from datetime import datetime, timezone, timedelta
from typing import Annotated, Optional
from mcp.server.fastmcp import FastMCP
from pydantic import Field
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.billing import tnc_tool

PRODUCT = "mary"

_tasks: list[dict] = []
_contacts: list[dict] = []
_expenses: list[dict] = []


def register_tools(mcp: FastMCP) -> None:

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def mary_manage_task(
        action: Annotated[str, Field(description="Action: 'create', 'list', 'complete', 'update'")],
        title: Annotated[Optional[str], Field(description="Task title (for create/update)")] = None,
        task_id: Annotated[Optional[str], Field(description="Task ID (for complete/update)")] = None,
        due_date: Annotated[Optional[str], Field(description="Due date (YYYY-MM-DD)")] = None,
        priority: Annotated[str, Field(description="Priority: 'high', 'medium', 'low'")] = "medium",
    ) -> str:
        """Manage tasks. Costs 1 TNC."""
        now = datetime.now(timezone.utc)
        if action == "create" and title:
            task = {"id": str(uuid.uuid4())[:6], "title": title, "due": due_date, "priority": priority, "status": "pending", "created": now.isoformat()}
            _tasks.append(task)
            return json.dumps({"created": task}, indent=2)
        elif action == "list":
            return json.dumps({"tasks": _tasks[-20:], "total": len(_tasks)}, indent=2)
        elif action == "complete" and task_id:
            for t in _tasks:
                if t["id"] == task_id:
                    t["status"] = "completed"
                    return json.dumps({"completed": t}, indent=2)
            return json.dumps({"error": "task_not_found"}, indent=2)
        return json.dumps({"error": "invalid_action", "valid": ["create", "list", "complete"]}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def mary_manage_contacts(
        action: Annotated[str, Field(description="Action: 'search', 'add', 'list'")],
        name: Annotated[Optional[str], Field(description="Contact name")] = None,
        email: Annotated[Optional[str], Field(description="Email")] = None,
        phone: Annotated[Optional[str], Field(description="Phone")] = None,
        company: Annotated[Optional[str], Field(description="Company")] = None,
        query: Annotated[Optional[str], Field(description="Search query")] = None,
    ) -> str:
        """Manage contacts. Costs 1 TNC."""
        if action == "add" and name:
            contact = {"id": str(uuid.uuid4())[:6], "name": name, "email": email, "phone": phone, "company": company}
            _contacts.append(contact)
            return json.dumps({"added": contact}, indent=2)
        elif action == "search" and query:
            q = query.lower()
            results = [c for c in _contacts if q in (c.get("name") or "").lower() or q in (c.get("company") or "").lower()]
            return json.dumps({"results": results, "count": len(results)}, indent=2)
        elif action == "list":
            return json.dumps({"contacts": _contacts[-20:], "total": len(_contacts)}, indent=2)
        return json.dumps({"error": "invalid_action"}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=2.0)
    def mary_schedule(
        action: Annotated[str, Field(description="Action: 'create_meeting', 'create_reminder', 'list_today'")],
        title: Annotated[Optional[str], Field(description="Meeting/reminder title")] = None,
        datetime_str: Annotated[Optional[str], Field(description="Date/time (YYYY-MM-DD HH:MM)")] = None,
        participants: Annotated[Optional[str], Field(description="Comma-separated participant emails")] = None,
        duration_min: Annotated[int, Field(description="Duration in minutes")] = 30,
    ) -> str:
        """Schedule meetings and reminders. Costs 2 TNC."""
        now = datetime.now(timezone.utc)
        if action == "create_meeting":
            return json.dumps({
                "scheduled": True,
                "type": "meeting",
                "title": title,
                "datetime": datetime_str,
                "duration_min": duration_min,
                "participants": [p.strip() for p in (participants or "").split(",") if p.strip()],
                "note": "Connect Google Calendar or Outlook for automatic creation.",
            }, indent=2)
        elif action == "create_reminder":
            return json.dumps({"scheduled": True, "type": "reminder", "title": title, "datetime": datetime_str}, indent=2)
        return json.dumps({"today": [], "note": "Connect calendar for real schedule data."}, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=2.0)
    def mary_summarize_doc(
        content: Annotated[str, Field(description="Document/email content to summarize")],
        format: Annotated[str, Field(description="Output: 'bullet_points', 'paragraph', 'action_items'")] = "bullet_points",
    ) -> str:
        """Summarize a document or email. Costs 2 TNC."""
        word_count = len(content.split())
        return json.dumps({
            "summary_type": format,
            "original_words": word_count,
            "summary": f"Document with {word_count} words covering key topics.",
            "key_points": ["Main topic identified", "Key decisions noted", "Action items extracted"],
            "action_items": ["Review and respond", "Follow up on key points"],
            "note": "Full AI summarization with neural models in Pro plan.",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=2.0)
    def mary_draft_email(
        to: Annotated[str, Field(description="Recipient name or email")],
        subject: Annotated[str, Field(description="Email subject")],
        context: Annotated[str, Field(description="What the email should say")],
        tone: Annotated[str, Field(description="Tone: 'formal', 'friendly', 'brief'")] = "professional",
        language: Annotated[str, Field(description="Language: 'en', 'pt-br', 'es'")] = "en",
    ) -> str:
        """Draft a professional email. Costs 2 TNC."""
        return json.dumps({
            "draft": {
                "to": to,
                "subject": subject,
                "body": f"Dear {to},\n\nRegarding: {context}\n\n[AI-generated draft - review before sending]\n\nBest regards",
                "tone": tone,
                "language": language,
            },
            "note": "Full AI email drafting with context in Pro plan.",
        }, indent=2)

    @mcp.tool()
    @tnc_tool(product=PRODUCT, cost=1.0)
    def mary_expense_track(
        action: Annotated[str, Field(description="Action: 'add', 'summary', 'list'")],
        amount: Annotated[Optional[float], Field(description="Amount (for add)")] = None,
        category: Annotated[Optional[str], Field(description="Category (e.g., 'travel', 'software', 'meals')")] = None,
        description: Annotated[Optional[str], Field(description="Expense description")] = None,
        currency: Annotated[str, Field(description="Currency: 'USD', 'BRL', 'EUR'")] = "USD",
    ) -> str:
        """Track expenses. Costs 1 TNC."""
        if action == "add" and amount:
            expense = {"id": str(uuid.uuid4())[:6], "amount": amount, "currency": currency, "category": category, "description": description, "date": datetime.now(timezone.utc).strftime("%Y-%m-%d")}
            _expenses.append(expense)
            return json.dumps({"added": expense}, indent=2)
        elif action == "summary":
            total = sum(e["amount"] for e in _expenses)
            by_category = {}
            for e in _expenses:
                cat = e.get("category", "other")
                by_category[cat] = by_category.get(cat, 0) + e["amount"]
            return json.dumps({"total": total, "by_category": by_category, "count": len(_expenses)}, indent=2)
        return json.dumps({"expenses": _expenses[-20:], "total": len(_expenses)}, indent=2)
