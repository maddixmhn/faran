"""Faran local mock university workflow; Python standard library only."""
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

STATE = Path(".faran/state.json")
ACTIVE = [
    "university_coordinator", "security_department_head", "hardening_professor",
    "teaching_assistant", "instructional_designer", "registrar", "lab_specialist",
    "it_coordinator", "cost_analyst", "hr_capacity_analyst", "draft_marketer", "independent_evaluator",
]

def load():
    if not STATE.exists():
        return {"roles": [], "runs": {}, "schedule": {"enabled": False}, "mode": "mock"}
    return json.loads(STATE.read_text(encoding="utf-8"))

def save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def seed(s):
    existing = {x["id"] for x in s["roles"]}
    for i in range(1, 2001):
        rid = f"role-{i:04d}"
        if rid not in existing:
            s["roles"].append({"id": rid, "title": ACTIVE[i-1] if i <= 12 else f"synthetic_specialist_{i:04d}", "active": i <= 12, "unit": "mock"})
    s["roles"].sort(key=lambda x: x["id"])
    return len(s["roles"])

def run(s, task_id):
    if task_id not in s["runs"]:
        s["runs"][task_id] = {"task_id": task_id, "status": "completed", "mode": "mock", "schedule_enabled": False,
          "course": "Offline Hardening Lab", "enrollment": {"synthetic": True, "count": 3},
          "exercise": {"fixture": "offline-baseline-v1", "findings": ["missing_security_header"], "real_scan": False},
          "marketing": {"status": "draft", "published": False}, "cost_usd": 0,
          "created_at": "2026-11-22T00:00:00Z"}
    return s["runs"][task_id]

def evaluate(r):
    ok = (r.get("mode") == "mock" and r.get("exercise", {}).get("real_scan") is False
          and r.get("marketing", {}).get("published") is False and r.get("cost_usd") == 0
          and isinstance(r.get("enrollment", {}).get("count"), int))
    return {"evaluator": "deterministic-independent-v1", "status": "pass" if ok else "fail",
            "checks": {"mock_only": r.get("mode") == "mock", "offline_fixture": r.get("exercise", {}).get("real_scan") is False,
                       "marketing_unpublished": r.get("marketing", {}).get("published") is False,
                       "zero_mock_cost": r.get("cost_usd") == 0}}

def main():
    p = argparse.ArgumentParser(description="فاران: گردش‌کار آزمایشی محلی")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("seed"); sub.add_parser("run").add_argument("--task-id", default="hardening-course-demo")
    sub.add_parser("status")
    a = p.parse_args(); s = load()
    if a.cmd == "seed":
        n = seed(s); save(s); out = {"mode":"mock", "roles":n, "active_sample_roles":12}
    elif a.cmd == "run":
        r = run(s, a.task_id); r["evaluation"] = evaluate(r); save(s); out = r
    else: out = {"mode":s["mode"], "roles":len(s["roles"]), "runs":len(s["runs"]), "schedule":s["schedule"]}
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))

if __name__ == "__main__": main()
