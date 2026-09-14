from agent_framework import ConcurrentBuilder

from agents.discipline_agents import create_discipline_agent


def build_concurrent_workflow():
    participants = [
        create_discipline_agent("Surveyor"),
        create_discipline_agent("Architect"),
        create_discipline_agent("Structural"),
        create_discipline_agent("HVAC"),
        create_discipline_agent("Electrical"),
        create_discipline_agent("Interior"),
    ]

    return (
        ConcurrentBuilder()
        .participants(participants)
        .build()
    )
