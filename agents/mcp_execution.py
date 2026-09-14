from agent_framework import Agent, MCPStreamableHTTPTool

from config import REVIT_MCP_URL
from .common import create_client


def create_revit_execution_agent(mcp_tool):
    return Agent(
        client=create_client(),
        name="RevitExecutionAgent",
        instructions="""
You are the Revit Execution Agent.

You may only act after the Python host has verified the explicit
human engineering approval gate.

Use ONLY the local Revit MCP tools supplied to you.

Before editing:
- inspect available MCP tools;
- inspect model state where possible;
- never invent element IDs;
- never delete unrelated content;
- make only requested/approved changes;
- report every tool call and model change.

Never make an independent engineering approval decision.
Never expose the Revit model outside the local/private boundary.

Return:
PRECONDITIONS
TOOLS USED
MODEL CHANGES
MODEL STATE
WARNINGS
FAILURES
""",
        tools=mcp_tool,
    )


def create_revit_mcp():
    return MCPStreamableHTTPTool(
        name="local-revit-mcp",
        url=REVIT_MCP_URL,
        load_tools=True,
        load_prompts=True,
        request_timeout=120,
        timeout=120,
        sse_read_timeout=120,
        # Keep this set to never_require here because the application-level
        # engineering approval gate occurs BEFORE this tool is created.
        # If your MCP bridge exposes destructive tools, you should additionally
        # configure approval_mode="always_require" for production.
    )
