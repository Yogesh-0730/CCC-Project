from __future__ import annotations

from typing import Any

from .algorithms import dp_01_knapsack, fractional_knapsack
from .utils import format_inr, option_ratio, option_roi, to_percent


def _compact_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "method": result["method"],
        "key": result["key"],
        "totalValue": result["totalValue"],
        "used": result["used"],
        "remaining": result["remaining"],
        "roi": result["roi"],
        "selectionCount": result["selectionCount"],
        "note": result["note"],
        "picks": [
            {
                "name": pick["name"],
                "fraction": float(pick["fraction"]),
                "pickedCost": int(pick["pickedCost"]),
                "pickedValue": float(pick["pickedValue"]),
            }
            for pick in result["picks"]
        ],
    }


def _option_performance_table(items: list[dict[str, Any]], budget: int) -> list[dict[str, Any]]:
    total_cost = sum(item["cost"] for item in items)
    rows: list[dict[str, Any]] = []

    ordered = sorted(items, key=option_ratio, reverse=True)
    for rank, item in enumerate(ordered, start=1):
        ratio = option_ratio(item)
        roi = option_roi(item)
        rows.append(
            {
                "rank": rank,
                "name": item["name"],
                "cost": item["cost"],
                "value": item["value"],
                "ratio": ratio,
                "roi": roi,
                "costShare": (item["cost"] / total_cost) if total_cost > 0 else 0.0,
                "budgetPressure": (item["cost"] / budget) if budget > 0 else 0.0,
            }
        )

    return rows


def _method_performance_table(results: list[dict[str, Any]], budget: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for result in results:
        utilization = (result["used"] / budget) if budget > 0 else 0.0
        rows.append(
            {
                "method": result["method"],
                "totalReturn": result["totalValue"],
                "budgetUsed": result["used"],
                "budgetLeft": result["remaining"],
                "utilization": utilization,
                "roi": result["roi"],
                "selectionCount": result["selectionCount"],
            }
        )
    return rows


def _comparison_payload(fractional: dict[str, Any], dp_result: dict[str, Any]) -> dict[str, Any]:
    delta = fractional["totalValue"] - dp_result["totalValue"]

    if delta > 0:
        verdict = "Fractional returns more because partial allocation is allowed."
        winner = "Greedy Fractional Knapsack"
    elif delta < 0:
        verdict = "DP 0/1 returns more in this dataset while using full-lot selections."
        winner = "DP 0/1 Knapsack"
    else:
        verdict = "Both methods produce the same total return for this dataset."
        winner = "Tie"

    return {
        "delta": delta,
        "deltaAbs": abs(delta),
        "fractionalRoi": fractional["roi"],
        "dpRoi": dp_result["roi"],
        "winner": winner,
        "verdict": verdict,
    }


def _charts_payload(
    *,
    items: list[dict[str, Any]],
    results: list[dict[str, Any]],
    budget: int,
    dp_result: dict[str, Any] | None,
) -> dict[str, Any]:
    cost_labels = [item["name"] for item in items]
    cost_values = [item["cost"] for item in items]
    return_values = [item["value"] for item in items]
    ratio_values = [option_ratio(item) for item in items]

    method_labels = [result["method"] for result in results]
    method_returns = [result["totalValue"] for result in results]

    max_return = max(method_returns) if method_returns else 1.0
    max_roi = max((result["roi"] for result in results), default=0.0001)
    max_selection = max((result["selectionCount"] for result in results), default=1)

    radar_labels = ["Return Strength", "Budget Utilization", "ROI Efficiency", "Diversification"]
    radar_datasets: list[dict[str, Any]] = []
    for result in results:
        radar_datasets.append(
            {
                "label": result["method"],
                "values": [
                    (result["totalValue"] / max_return) * 100 if max_return > 0 else 0.0,
                    (result["used"] / budget) * 100 if budget > 0 else 0.0,
                    (result["roi"] / max_roi) * 100 if max_roi > 0 else 0.0,
                    (result["selectionCount"] / max_selection) * 100 if max_selection > 0 else 0.0,
                ],
            }
        )

    allocation_pies: list[dict[str, Any]] = []
    for result in results:
        labels = [pick["name"] for pick in result["picks"]]
        values = [pick["pickedCost"] for pick in result["picks"]]
        if not labels:
            labels = ["No allocation"]
            values = [1]
        allocation_pies.append(
            {
                "method": result["method"],
                "labels": labels,
                "values": values,
            }
        )

    dp_line = {
        "labels": [point["capacityUnit"] for point in (dp_result["curve"] if dp_result else [])],
        "values": [point["maxValue"] for point in (dp_result["curve"] if dp_result else [])],
    }

    return {
        "portfolioCostPie": {"labels": cost_labels, "values": cost_values},
        "portfolioReturnPie": {"labels": cost_labels, "values": return_values},
        "ratioBar": {"labels": cost_labels, "values": ratio_values},
        "methodReturnBar": {"labels": method_labels, "values": method_returns},
        "methodRadar": {"labels": radar_labels, "datasets": radar_datasets},
        "allocationPies": allocation_pies,
        "dpValueCurve": dp_line,
    }


def _metrics_payload(
    *,
    items: list[dict[str, Any]],
    budget: int,
    results: list[dict[str, Any]],
    comparison: dict[str, Any] | None,
) -> dict[str, Any]:
    total_required = sum(item["cost"] for item in items)
    total_potential = sum(item["value"] for item in items)
    avg_roi = sum(option_roi(item) for item in items) / len(items)
    best_option = max(items, key=option_ratio)

    coverage = min((budget / total_required), 1.0) if total_required > 0 else 0.0
    overbook_ratio = (total_required / budget) if budget > 0 else 0.0

    winner = "Not run"
    if comparison:
        winner = comparison["winner"]
    elif results:
        best_result = max(results, key=lambda row: row["totalValue"])
        winner = best_result["method"]

    return {
        "coverageText": f"{to_percent(coverage)} of listed capital ({format_inr(budget)})",
        "potentialText": format_inr(total_potential),
        "averageRoiText": to_percent(avg_roi),
        "bestText": f"{best_option['name']} ({option_ratio(best_option):.2f}x)",
        "winnerText": winner,
        "totalRequired": total_required,
        "totalPotential": total_potential,
        "averageRoi": avg_roi,
        "coverage": coverage,
        "overbookRatio": overbook_ratio,
    }


def analyze_portfolio(
    *,
    mode: str,
    budget: int,
    items: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    results: list[dict[str, Any]] = []
    comparison: dict[str, Any] | None = None
    fractional_result: dict[str, Any] | None = None
    dp_result: dict[str, Any] | None = None

    if mode == "fractional":
        fractional_result = fractional_knapsack(items, budget)
        results = [fractional_result]
    elif mode == "dp01":
        dp_result = dp_01_knapsack(items, budget)
        results = [dp_result]
    elif mode == "compare":
        fractional_result = fractional_knapsack(items, budget)
        dp_result = dp_01_knapsack(items, budget)
        results = [fractional_result, dp_result]
        comparison = _comparison_payload(fractional_result, dp_result)

    metrics = _metrics_payload(items=items, budget=budget, results=results, comparison=comparison)
    option_table = _option_performance_table(items, budget)
    method_table = _method_performance_table(results, budget)

    guides = {
        "fractional": {
            "title": "Greedy Fractional Knapsack",
            "strategy": "Sort options by value/cost ratio and invest greedily, allowing fractions.",
            "timeComplexity": "O(n log n)",
            "spaceComplexity": "O(n)",
        },
        "dp01": {
            "title": "Dynamic Programming 0/1 Knapsack",
            "strategy": "Build a DP table where each state tracks the best value for a given prefix and capacity.",
            "timeComplexity": "O(n * W)",
            "spaceComplexity": "O(n * W)",
            "scaledCapacity": dp_result["scaledCapacity"] if dp_result else None,
            "scaleFactor": dp_result["scaleFactor"] if dp_result else None,
            "tableCells": dp_result["tableCells"] if dp_result else None,
        },
    }

    response = {
        "budget": budget,
        "mode": mode,
        "options": items,
        "metrics": metrics,
        "results": [_compact_result(result) for result in results],
        "comparison": comparison,
        "tables": {
            "optionPerformance": option_table,
            "methodPerformance": method_table,
            "fractionalTrace": fractional_result["trace"] if fractional_result else [],
            "dpTrace": dp_result["trace"] if dp_result else [],
        },
        "charts": _charts_payload(items=items, results=results, budget=budget, dp_result=dp_result),
        "guides": guides,
    }

    run_log: dict[str, Any] | None = None
    if mode != "insights":
        fractional_value = fractional_result["totalValue"] if fractional_result else None
        dp_value = dp_result["totalValue"] if dp_result else None
        winner = metrics["winnerText"]
        utilization = max((result["used"] / budget) for result in results) if results and budget > 0 else 0.0

        run_log = {
            "mode": mode,
            "budget": budget,
            "optionCount": len(items),
            "fractionalValue": fractional_value,
            "dpValue": dp_value,
            "winner": winner,
            "utilization": utilization,
            "notes": "Algorithm run recorded by analysis service.",
        }

    return response, run_log
