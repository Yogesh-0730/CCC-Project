from __future__ import annotations

from datetime import datetime, timezone
import uuid
from typing import Any

from .constants import SAMPLE_OPTIONS
from .database import load_db, save_db
from .utils import parse_money


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _clean_option(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(record["id"]),
        "name": str(record["name"]),
        "cost": int(record["cost"]),
        "value": int(record["value"]),
        "createdAt": str(record["createdAt"]),
    }


def list_options() -> list[dict[str, Any]]:
    db = load_db()
    options = [_clean_option(item) for item in db["options"]]
    options.sort(key=lambda item: (item["createdAt"], item["name"].lower()))
    return options


def add_option(*, name: str, cost_raw: Any, value_raw: Any) -> dict[str, Any]:
    cleaned_name = name.strip()
    if not cleaned_name:
        raise ValueError("Option name is required.")

    cost = parse_money(cost_raw, field="required amount")
    value = parse_money(value_raw, field="expected return")

    db = load_db()
    option = {
        "id": str(uuid.uuid4()),
        "name": cleaned_name,
        "cost": cost,
        "value": value,
        "createdAt": _now_iso(),
    }
    db["options"].append(option)
    save_db(db)
    return option


def delete_option(option_id: str) -> bool:
    db = load_db()
    before = len(db["options"])
    db["options"] = [item for item in db["options"] if str(item.get("id")) != option_id]
    after = len(db["options"])

    if before == after:
        return False

    save_db(db)
    return True


def replace_options(options: list[dict[str, Any]]) -> list[dict[str, Any]]:
    db = load_db()
    now = _now_iso()

    db["options"] = [
        {
            "id": str(uuid.uuid4()),
            "name": str(item["name"]),
            "cost": int(item["cost"]),
            "value": int(item["value"]),
            "createdAt": now,
        }
        for item in options
    ]
    save_db(db)
    return list_options()


def ensure_seed_data() -> None:
    db = load_db()
    if db["options"]:
        return

    now = _now_iso()
    db["options"] = [
        {
            "id": str(uuid.uuid4()),
            "name": str(item["name"]),
            "cost": int(item["cost"]),
            "value": int(item["value"]),
            "createdAt": now,
        }
        for item in SAMPLE_OPTIONS
    ]
    save_db(db)


def reset_to_sample() -> list[dict[str, Any]]:
    return replace_options(SAMPLE_OPTIONS)


def log_analysis_run(payload: dict[str, Any]) -> None:
    db = load_db()
    next_id = int(db["meta"].get("next_history_id", 1))

    entry = {
        "id": next_id,
        "runAt": _now_iso(),
        "mode": str(payload.get("mode", "unknown")),
        "budget": int(payload.get("budget", 0)),
        "optionCount": int(payload.get("optionCount", 0)),
        "fractionalValue": payload.get("fractionalValue"),
        "dpValue": payload.get("dpValue"),
        "winner": payload.get("winner"),
        "utilization": payload.get("utilization"),
        "notes": payload.get("notes"),
    }

    db["analysis_runs"].append(entry)
    db["meta"]["next_history_id"] = next_id + 1
    save_db(db)


def list_analysis_runs(limit: int = 20) -> list[dict[str, Any]]:
    safe_limit = max(1, min(limit, 100))
    db = load_db()

    rows = sorted(db["analysis_runs"], key=lambda row: int(row["id"]), reverse=True)
    rows = rows[:safe_limit]

    cleaned: list[dict[str, Any]] = []
    for row in rows:
        cleaned.append(
            {
                "id": int(row["id"]),
                "runAt": str(row["runAt"]),
                "mode": str(row["mode"]),
                "budget": int(row["budget"]),
                "optionCount": int(row["optionCount"]),
                "fractionalValue": float(row["fractionalValue"]) if row["fractionalValue"] is not None else None,
                "dpValue": float(row["dpValue"]) if row["dpValue"] is not None else None,
                "winner": row["winner"],
                "utilization": float(row["utilization"]) if row["utilization"] is not None else None,
                "notes": row["notes"],
            }
        )

    return cleaned
