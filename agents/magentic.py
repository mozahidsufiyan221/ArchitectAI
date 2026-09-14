from agent_framework import Agent, MagenticBuilder

from .common import create_client
from .discipline_agents import create_discipline_agent


def create_manager_agent():
    return Agent(
        client=create_client(),
        name="AECManager",
        instructions="""
You are the Magentic manager for a Saudi Arabian AEC consulting project.

Coordinate these discipline agents:
- Surveyor
- Architect
- Structural
- HVAC
- Electrical
- Interior

Your task is to plan, delegate, monitor progress and synthesize the
multidisciplinary preliminary design.

You must:
- identify dependencies;
- request survey/site information before relying on site assumptions;
- allow independent discipline work to proceed where appropriate;
- detect contradictions;
- request clarification when needed;
- never approve engineering work;
- never modify Revit.

The output must clearly distinguish:
PROPOSED
REQUIRES REVIEW
APPROVED BY HUMAN
EXECUTED

Final engineering approval belongs to the human SCE-registered reviewer.
""",
    )


def build_magentic_workflow():
    manager = create_manager_agent()

    participants = [
        create_discipline_agent("Surveyor"),
        create_discipline_agent("Architect"),
        create_discipline_agent("Structural"),
        create_discipline_agent("HVAC"),
        create_discipline_agent("Electrical"),
        create_discipline_agent("Interior"),
    ]

    workflow = (
        MagenticBuilder()
        .participants(*participants)
        .with_standard_manager(
            agent=manager,
            max_round_count=12,
            max_stall_count=3,
        )
        .build()
    )

    return workflow
