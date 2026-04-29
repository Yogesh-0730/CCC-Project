from __future__ import annotations

import math
from typing import Any

from .utils import option_ratio


def fractional_knapsack(items: list[dict[str, Any]], capacity: int) -> dict[str, Any]:
    sorted_items = sorted(items, key=option_ratio, reverse=True)

    remaining = capacity
    total_value = 0.0
    picks: list[dict[str, Any]] = []
    trace: list[dict[str, Any]] = []

    for step, item in enumerate(sorted_items, start=1):
        if remaining <= 0:
            break

        ratio = option_ratio(item)
        if item["cost"] <= remaining:
            fraction = 1.0
            invested = item["cost"]
            gained = float(item["value"])
        else:
            fraction = remaining / item["cost"]
            invested = remaining
            gained = item["value"] * fraction

        remaining -= invested
        total_value += gained

        picks.append(
            {
                "id": item["id"],
                "name": item["name"],
                "fraction": fraction,
                "pickedCost": invested,
                "pickedValue": gained,
            }
        )

        trace.append(
            {
                "step": step,
                "name": item["name"],
                "cost": item["cost"],
                "value": item["value"],
                "ratio": ratio,
                "takenFraction": fraction,
                "invested": invested,
                "gained": gained,
                "remainingBudget": remaining,
            }
        )

    used = capacity - remaining
    roi = (total_value - used) / used if used > 0 else 0.0

    return {
        "method": "Greedy Fractional Knapsack",
        "key": "fractional",
        "totalValue": total_value,
        "used": used,
        "remaining": remaining,
        "roi": roi,
        "selectionCount": len(picks),
        "picks": picks,
        "note": "Greedy sorting by value/cost ratio allows partial investments.",
        "trace": trace,
        "complexity": {
            "time": "O(n log n)",
            "space": "O(n)",
        },
    }


def dp_01_knapsack(items: list[dict[str, Any]], capacity: int, max_weight: int = 6000) -> dict[str, Any]:
    scale_factor = math.ceil(capacity / max_weight) if capacity > max_weight else 1
    scaled_capacity = max(0, capacity // scale_factor)

    scaled_items: list[dict[str, Any]] = []
    for item in items:
        scaled_cost = max(1, math.ceil(item["cost"] / scale_factor))
        scaled_items.append({**item, "scaledCost": scaled_cost})

    n = len(scaled_items)
    dp = [[0] * (scaled_capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        item = scaled_items[i - 1]
        for w in range(scaled_capacity + 1):
            if item["scaledCost"] > w:
                dp[i][w] = dp[i - 1][w]
            else:
                keep = dp[i - 1][w]
                take = dp[i - 1][w - item["scaledCost"]] + item["value"]
                dp[i][w] = max(keep, take)

    picks: list[dict[str, Any]] = []
    picked_ids: set[str] = set()
    w = scaled_capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            item = scaled_items[i - 1]
            picked_ids.add(item["id"])
            picks.append(
                {
                    "id": item["id"],
                    "name": item["name"],
                    "fraction": 1.0,
                    "pickedCost": item["cost"],
                    "pickedValue": float(item["value"]),
                }
            )
            w -= item["scaledCost"]

    picks.reverse()
    used = sum(int(item["pickedCost"]) for item in picks)
    remaining = max(0, capacity - used)
    total_value = float(dp[n][scaled_capacity])
    roi = (total_value - used) / used if used > 0 else 0.0

    trace: list[dict[str, Any]] = []
    for idx, item in enumerate(scaled_items, start=1):
        trace.append(
            {
                "step": idx,
                "name": item["name"],
                "cost": item["cost"],
                "value": item["value"],
                "scaledCost": item["scaledCost"],
                "selected": item["id"] in picked_ids,
            }
        )

    sample_step = max(1, scaled_capacity // 16) if scaled_capacity > 0 else 1
    sample_points = list(range(0, scaled_capacity + 1, sample_step))
    if sample_points[-1] != scaled_capacity:
        sample_points.append(scaled_capacity)

    curve = [{"capacityUnit": point, "maxValue": float(dp[n][point])} for point in sample_points]

    note = (
        f"0/1 DP used scaling factor {scale_factor} to keep matrix size practical in-browser."
        if scale_factor > 1
        else "Exact 0/1 dynamic programming over the full capacity table."
    )

    return {
        "method": "DP 0/1 Knapsack",
        "key": "dp01",
        "totalValue": total_value,
        "used": used,
        "remaining": remaining,
        "roi": roi,
        "selectionCount": len(picks),
        "picks": picks,
        "note": note,
        "trace": trace,
        "curve": curve,
        "scaleFactor": scale_factor,
        "scaledCapacity": scaled_capacity,
        "tableCells": (n + 1) * (scaled_capacity + 1),
        "complexity": {
            "time": "O(n * W)",
            "space": "O(n * W)",
        },
    }
