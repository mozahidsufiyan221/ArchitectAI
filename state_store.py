import json
from pathlib import Path

from config import PROJECTS_DIR
from models import ProjectState


def project_dir(project_id: str) -> Path:
    path = PROJECTS_DIR / project_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def state_path(project_id: str) -> Path:
    return project_dir(project_id) / "state.json"


def save_state(state: ProjectState):
    state_path(state.project_id).write_text(
        json.dumps(
            state.to_dict(),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def load_state(project_id: str) -> ProjectState:
    data = json.loads(
        state_path(project_id).read_text(encoding="utf-8")
    )

    state = ProjectState(
        project_id=data["project_id"],
        client_brief=data.get("client_brief", ""),
        status=data.get("status", "brief"),
    )

    for key, value in data.items():
        if key in {"project_id", "client_brief", "status"}:
            continue
        if hasattr(state, key):
            setattr(state, key, value)

    return state


def write_artifact(project_id: str, relative_path: str, content: str):
    path = project_dir(project_id) / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
