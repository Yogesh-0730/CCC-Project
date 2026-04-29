from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from backend.analysis_service import analyze_portfolio
from backend.constants import VALID_MODES
from backend.database import init_db
from backend.repository import (
    add_option,
    delete_option,
    ensure_seed_data,
    list_analysis_runs,
    list_options,
    log_analysis_run,
    reset_to_sample,
)
from backend.utils import parse_money

app = Flask(__name__)
init_db()
ensure_seed_data()


def _error(message: str, status: int = 400):
    return jsonify({"ok": False, "error": message}), status


@app.get("/")
def home() -> str:
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"ok": True})


@app.get("/api/bootstrap")
def bootstrap_data():
    ensure_seed_data()
    return jsonify({"ok": True, "options": list_options(), "history": list_analysis_runs(limit=20)})


@app.get("/api/options")
def get_options():
    ensure_seed_data()
    return jsonify({"ok": True, "options": list_options()})


@app.post("/api/options")
def create_option():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error("Request body must be a JSON object.")

    try:
        add_option(
            name=str(payload.get("name", "")).strip(),
            cost_raw=payload.get("cost"),
            value_raw=payload.get("value"),
        )
    except ValueError as exc:
        return _error(str(exc))

    return jsonify({"ok": True, "options": list_options()})


@app.delete("/api/options/<option_id>")
def remove_option(option_id: str):
    deleted = delete_option(option_id)
    if not deleted:
        return _error("Option not found.", 404)

    return jsonify({"ok": True, "options": list_options()})


@app.post("/api/options/reset")
def reset_options():
    options = reset_to_sample()
    return jsonify({"ok": True, "options": options})


@app.get("/api/history")
def get_history():
    limit_raw = request.args.get("limit", default="20")
    try:
        limit = max(1, min(100, int(limit_raw)))
    except ValueError:
        return _error("Limit must be an integer.")

    return jsonify({"ok": True, "history": list_analysis_runs(limit=limit)})


@app.post("/api/analyze")
def analyze():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _error("Request body must be a JSON object.")

    mode = str(payload.get("mode", "compare")).strip().lower()
    if mode not in VALID_MODES:
        return _error("Invalid mode. Choose fractional, dp01, compare, or insights.")

    try:
        budget = parse_money(payload.get("budget"), field="budget")
    except ValueError as exc:
        return _error(str(exc))

    ensure_seed_data()
    options = list_options()
    if not options:
        return _error("No options found. Add options first.")

    data, run_log = analyze_portfolio(mode=mode, budget=budget, items=options)
    if run_log is not None:
        log_analysis_run(run_log)

    history = list_analysis_runs(limit=20)
    return jsonify({"ok": True, **data, "history": history})


if __name__ == "__main__":
    app.run(debug=True)
