from agent_framework import ConcurrentBuilder

from agents.surveyor import create_surveyor
from agents.architect import create_architect
from agents.structural import create_structural
from agents.hvac import create_hvac
from agents.electrical import create_electrical
from agents.interior import create_interior
from agents.reviewer import create_reviewer


async def run_parallel_design(project_brief: str):

    surveyor = create_surveyor()
    architect = create_architect()
    structural = create_structural()
    hvac = create_hvac()
    electrical = create_electrical()
    interior = create_interior()

    workflow = (
        ConcurrentBuilder()
        .participants([
            surveyor,
            architect,
            structural,
            hvac,
            electrical,
            interior,
        ])
        .build()
    )

    result = await workflow.run(project_brief)

    return result


async def run_review(project_package: str):

    reviewer = create_reviewer()

    result = await reviewer.run(
        project_package
    )

    return result