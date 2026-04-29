from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "planner_db.json"
_DB_LOCK = Lock()


def _default_db() -> dict[str, Any]:
    return {
        "meta": {"next_history_id": 1},
        "options": [],
        "analysis_runs": [],
    }


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        save_db(_default_db())


def load_db() -> dict[str, Any]:
    init_db()
    with _DB_LOCK:
        try:
            data = json.loads(DB_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = _default_db()
            save_db(data)

    if not isinstance(data, dict):
        data = _default_db()
        save_db(data)

    data.setdefault("meta", {"next_history_id": 1})
    data.setdefault("options", [])
    data.setdefault("analysis_runs", [])
    if "next_history_id" not in data["meta"]:
        data["meta"]["next_history_id"] = 1
    return data


def save_db(data: dict[str, Any]) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with _DB_LOCK:
        DB_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
