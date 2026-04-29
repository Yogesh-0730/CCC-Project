from __future__ import annotations

import math
import re
from typing import Any

MONEY_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)(k|l|cr)?$")


def parse_money(raw: Any, *, field: str) -> int:
    if raw is None:
        raise ValueError(f"Missing {field}.")

    if isinstance(raw, bool):
        raise ValueError(f"Invalid {field}.")

    if isinstance(raw, (int, float)):
        if isinstance(raw, float) and (math.isnan(raw) or math.isinf(raw)):
            raise ValueError(f"Invalid {field}.")
        amount = float(raw)
    else:
        text = str(raw).strip().lower().replace(",", "")
        if not text:
            raise ValueError(f"Missing {field}.")

        match = MONEY_PATTERN.fullmatch(text)
        if match:
            base = float(match.group(1))
            unit = match.group(2)
            factor = 1
            if unit == "k":
                factor = 1_000
            elif unit == "l":
                factor = 100_000
            elif unit == "cr":
                factor = 10_000_000
            amount = base * factor
        else:
            try:
                amount = float(text)
            except ValueError as exc:
                raise ValueError(f"Invalid {field} format.") from exc

    rounded = int(round(amount))
    if rounded <= 0:
        raise ValueError(f"{field.capitalize()} must be positive.")
    return rounded


def option_ratio(item: dict[str, Any]) -> float:
    return item["value"] / item["cost"]


def option_roi(item: dict[str, Any]) -> float:
    return (item["value"] - item["cost"]) / item["cost"]


def to_percent(value: float, digits: int = 1) -> str:
    return f"{value * 100:.{digits}f}%"


def format_inr(amount: float) -> str:
    value = int(round(amount))
    sign = "-" if value < 0 else ""
    value = abs(value)
    digits = str(value)

    if len(digits) <= 3:
        grouped = digits
    else:
        head = digits[:-3]
        tail = digits[-3:]
        chunks: list[str] = []
        while len(head) > 2:
            chunks.insert(0, head[-2:])
            head = head[:-2]
        if head:
            chunks.insert(0, head)
        grouped = ",".join(chunks + [tail])

    return f"{sign}Rs {grouped}"
