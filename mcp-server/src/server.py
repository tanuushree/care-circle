"""Care Circle MCP server entrypoint.

Exposes medication/appointment/care-circle tools to Alexa+ over
Streamable HTTP, per MCP spec 2025-11-25.

Run locally:
    python src/server.py

"""
import os
from dotenv import load_dotenv
from fastmcp import FastMCP
from circle_auth.auth import SupabaseTokenVerifier

from tools.log_medication_taken import log_medication_taken
from tools.get_schedule import get_medication_schedule
from tools.get_upcoming_appointments import get_upcoming_appointments
from tools.get_refill_status import get_refill_status
from tools.add_care_note import add_care_note
from tools.trigger_sos import trigger_sos

from circle_auth.auth_context import get_authenticated_user_id
from circle_auth.circle_context import get_user_circle_id

load_dotenv()

auth = SupabaseTokenVerifier()
mcp = FastMCP("care-circle", auth=auth,)


@mcp.tool()
def log_medication(circle_id: str, drug_name: str, user_id: str) -> dict:
    """Log that a medication was just taken."""
    return log_medication_taken(circle_id, drug_name, user_id)


@mcp.tool()
def get_schedule() -> dict:
    """Get today's medication schedule for the authenticated user's care circle."""
    user_id = get_authenticated_user_id()
    circle_id = get_user_circle_id(user_id)
    return get_medication_schedule(circle_id)


@mcp.tool()
def get_appointments(circle_id: str) -> dict:
    """Get upcoming doctor appointments for a care circle."""
    return get_upcoming_appointments(circle_id)


@mcp.tool()
def get_refills(circle_id: str) -> dict:
    """Check which medications are running low and need a refill."""
    return get_refill_status(circle_id)


@mcp.tool()
def add_note(circle_id: str, author_user_id: str, note: str) -> dict:
    """Leave a note for other members of the care circle."""
    return add_care_note(circle_id, author_user_id, note)


@mcp.tool()
def sos(circle_id: str, triggered_by_user_id: str) -> dict:
    """Trigger an emergency SOS alert to all circle members."""
    return trigger_sos(circle_id, triggered_by_user_id)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    mcp.run(transport="streamable-http", port=port)
