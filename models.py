from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Literal


ProjectStatus = Literal[
    "brief",
    "planning",
    "plan_review",
    "plan_approved",
    "design",
    "review",
    "qa_approved",
    "rejected",
    "executing",
    "completed",
    "execution_failed",
]


@dataclass
class ProjectState:
    project_id: str
    client_brief: str = ""
    status: ProjectStatus = "brief"

    magentic_plan: str = ""
    discipline_results: str = ""
    reviewer_result: str = ""

    sbc_evidence: list[dict] = field(default_factory=list)

    plan_human_approved: bool = False
    engineering_human_approved: bool = False

    execution_result: str = ""

    audit: list[dict] = field(default_factory=list)

    def record(self, event: str, **details):
        self.audit.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            **details,
        })

    def to_dict(self):
        return asdict(self)
