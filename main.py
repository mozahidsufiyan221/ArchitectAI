import argparse
import asyncio
from datetime import datetime
from pathlib import Path
import uuid

from models import ProjectState
from state_store import (
    load_state,
    save_state,
    write_artifact,
)

from workflows.concurrent_design import build_concurrent_workflow
from agents.magentic import build_magentic_workflow
from agents.reviewer import create_reviewer
from rag.sbc_rag import SBCRetriever


def approval_gate(title: str, details: str) -> bool:
    print("\n" + "=" * 88)
    print(title)
    print("=" * 88)
    print(details)
    print("=" * 88)

    response = input(
        "Type APPROVE to continue, or anything else to stop: "
    )

    return response.strip().upper() == "APPROVE"


async def run_magentic(state: ProjectState):
    workflow = build_magentic_workflow()

    prompt = f"""
PROJECT BRIEF:

{state.client_brief}

Create and manage a multidisciplinary preliminary AEC plan.

Do not execute Revit.
Do not claim regulatory approval.
Do not issue stamped engineering.

Return a structured project plan and the information required from
each discipline.
"""

    result = await workflow.run(prompt)
    return str(result)


async def run_concurrent(state: ProjectState):
    workflow = build_concurrent_workflow()

    prompt = f"""
CLIENT BRIEF:

{state.client_brief}

MAGENTIC MANAGER PLAN:

{state.magentic_plan}

Perform your discipline-specific preliminary analysis.

Rules:
- Do not invent missing site data.
- Do not issue stamped engineering.
- Do not modify Revit.
- Clearly identify assumptions and missing information.
"""

    result = await workflow.run(prompt)
    return str(result)


async def run_reviewer(state: ProjectState, sbc_context: str):
    reviewer = create_reviewer()

    prompt = f"""
CLIENT BRIEF:

{state.client_brief}

MAGENTIC PLAN:

{state.magentic_plan}

DISCIPLINE OUTPUTS:

{state.discipline_results}

LOCAL SBC RETRIEVAL EVIDENCE:

{sbc_context}

Review the multidisciplinary work.

Never invent SBC requirements.

If the retrieved evidence does not support a compliance claim,
state EVIDENCE NOT AVAILABLE.

Return a structured QA report and explicit human approval items.
"""

    result = await reviewer.run(prompt)
    return str(result)


async def run_revit(state: ProjectState):
    from agents.mcp_execution import (
        create_revit_execution_agent,
        create_revit_mcp,
    )

    mcp = create_revit_mcp()

    try:
        # Explicit application-level human gate has already passed.
        agent = create_revit_execution_agent(mcp)

        prompt = f"""
EXECUTION AUTHORIZATION:

Human engineering approval = TRUE.

PROJECT ID:
{state.project_id}

CLIENT BRIEF:
{state.client_brief}

APPROVED QA PACKAGE:
{state.reviewer_result}

Use only the local Revit MCP tools.

First inspect the available tools and current model state.

Then perform only the approved model changes.

Never invent element IDs.
Never delete unrelated content.
Report every meaningful model modification.

At the end provide:
PRECONDITIONS
TOOLS USED
MODEL CHANGES
MODEL STATE
WARNINGS
FAILURES
"""

        result = await agent.run(prompt)
        return str(result)

    finally:
        await mcp.close()


async def main():
    parser = argparse.ArgumentParser(
        description="Saudi AEC Microsoft Agent Framework system"
    )

    parser.add_argument("--brief")
    parser.add_argument("--brief-text")
    parser.add_argument("--project-id")
    parser.add_argument(
        "--skip-execution",
        action="store_true",
    )

    args = parser.parse_args()

    if args.brief_text:
        brief = args.brief_text.strip()

    elif args.brief:
        brief = Path(
            args.brief
        ).read_text(
            encoding="utf-8"
        )

    else:
        raise SystemExit(
            "Use --brief FILE or --brief-text TEXT"
        )

    project_id = (
        args.project_id
        or (
            datetime.now().strftime("%Y%m%d-%H%M%S")
            + "-"
            + uuid.uuid4().hex[:6]
        )
    )

    if args.project_id:
        try:
            state = load_state(project_id)
        except FileNotFoundError:
            state = ProjectState(
                project_id=project_id,
                client_brief=brief,
            )
    else:
        state = ProjectState(
            project_id=project_id,
            client_brief=brief,
        )

    print("=" * 88)
    print("AI-AUGMENTED AEC CONSULTING SYSTEM")
    print("Saudi Arabia Edition")
    print("Microsoft Agent Framework + LM Studio + Local Revit MCP")
    print("=" * 88)
    print(f"Project ID: {state.project_id}")

    # ---------------------------------------------------------
    # 1. MAGENTIC PLANNING
    # ---------------------------------------------------------

    if not state.magentic_plan:
        state.status = "planning"
        state.record("magentic_planning_started")
        save_state(state)

        print("\n[1] MAGENTIC BUILDER")
        print("Creating manager-driven multidisciplinary plan...")

        state.magentic_plan = await run_magentic(state)

        write_artifact(
            state.project_id,
            "supervisor/magentic_plan.txt",
            state.magentic_plan,
        )

        state.record("magentic_planning_completed")
        state.status = "plan_review"
        save_state(state)

    print("\n--- MAGENTIC PLAN ---")
    print(state.magentic_plan)

    # ---------------------------------------------------------
    # 2. HUMAN PLAN APPROVAL
    # ---------------------------------------------------------

    if not state.plan_human_approved:
        approved = approval_gate(
            "HUMAN PLAN APPROVAL",
            "Review the Magentic plan before the discipline fan-out.",
        )

        if not approved:
            state.status = "rejected"
            state.record("plan_human_approval_rejected")
            save_state(state)
            print("Stopped.")
            return

        state.plan_human_approved = True
        state.status = "plan_approved"
        state.record("plan_human_approved")
        save_state(state)

    # ---------------------------------------------------------
    # 3. CONCURRENT DISCIPLINES
    # ---------------------------------------------------------

    if not state.discipline_results:
        state.status = "design"
        state.record("concurrent_design_started")
        save_state(state)

        print("\n[2] CONCURRENT BUILDER")
        print(
            "Running Surveyor, Architect, Structural, HVAC, "
            "Electrical and Interior agents in parallel..."
        )

        state.discipline_results = await run_concurrent(state)

        write_artifact(
            state.project_id,
            "disciplines/concurrent_results.txt",
            state.discipline_results,
        )

        state.record("concurrent_design_completed")
        save_state(state)

    # ---------------------------------------------------------
    # 4. SBC RAG + REVIEWER
    # ---------------------------------------------------------

    if not state.reviewer_result:
        print("\n[3] SBC RAG + REVIEWER / QA")

        rag = SBCRetriever()

        query = f"""
Saudi Building Code evidence relevant to this project:

{state.client_brief}

Need evidence for architectural requirements, occupancy, egress,
accessibility, structural considerations, mechanical/HVAC,
electrical, fire/life safety and preliminary municipal/Balady readiness.
"""

        sbc_results = rag.search(query)
        sbc_context = rag.context(query)

        state.sbc_evidence = sbc_results

        write_artifact(
            state.project_id,
            "qa/sbc_retrieval.txt",
            sbc_context,
        )

        state.reviewer_result = await run_reviewer(
            state,
            sbc_context,
        )

        write_artifact(
            state.project_id,
            "qa/reviewer_report.txt",
            state.reviewer_result,
        )

        state.status = "review"
        state.record(
            "reviewer_completed",
            sbc_chunks=len(sbc_results),
        )
        save_state(state)

    print("\n--- REVIEWER / QA ---")
    print(state.reviewer_result)

    # ---------------------------------------------------------
    # 5. HUMAN ENGINEERING APPROVAL
    # ---------------------------------------------------------

    if not state.engineering_human_approved:
        approved = approval_gate(
            "SCE-REGISTERED HUMAN ENGINEERING APPROVAL",
            "Review the QA report and SBC evidence. "
            "Approval authorizes the Revit execution phase.",
        )

        if not approved:
            state.status = "rejected"
            state.record(
                "engineering_human_approval_rejected"
            )
            save_state(state)
            print("Stopped. Revit execution was NOT authorized.")
            return

        state.engineering_human_approved = True
        state.status = "qa_approved"
        state.record(
            "engineering_human_approved"
        )
        save_state(state)

    # ---------------------------------------------------------
    # 6. EXECUTION
    # ---------------------------------------------------------

    if args.skip_execution:
        print("\nExecution skipped (--skip-execution).")
        state.record("revit_execution_skipped")
        save_state(state)
        return

    print("\n[4] LOCAL REVIT MCP EXECUTION")

    state.status = "executing"
    state.record("revit_execution_started")
    save_state(state)

    try:
        state.execution_result = await run_revit(state)

        write_artifact(
            state.project_id,
            "execution/revit_result.txt",
            state.execution_result,
        )

        state.status = "completed"
        state.record(
            "revit_execution_completed"
        )
        save_state(state)

        print("\n--- REVIT EXECUTION RESULT ---")
        print(state.execution_result)

    except Exception as exc:
        state.status = "execution_failed"
        state.record(
            "revit_execution_failed",
            error=str(exc),
        )
        save_state(state)
        raise

    print("\n[5] COMPLETE")
    print(
        f"Project state: "
        f"data\\projects\\{state.project_id}\\state.json"
    )


if __name__ == "__main__":
    asyncio.run(main())
