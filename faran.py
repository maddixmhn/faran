"""Faran local mock university workflow; Python standard library only."""
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

STATE = Path(".faran/state.json")
ACTIVE = [
    "خانم بیات · مدیر ارشد دانشگاه", "دکتر فرخی · مدیر گروه فناوری اطلاعات",
    "دکتر شکراللی · مدیر گروه مهندسی کامپیوتر", "خانم کلهرودی · مدیر آموزش",
    "استاد هاردنینگ", "دستیار آموزشی", "طراح آموزشی", "کارشناس آموزش و ثبت‌نام",
    "متخصص آزمایشگاه محکم‌بان", "هماهنگ‌کنندهٔ IT", "تحلیلگر هزینه",
    "کارشناس ظرفیت منابع انسانی", "پیش‌نویس‌نویس معرفی درس", "ارزیاب مستقل دکتر سلیمانی",
]

def load():
    if not STATE.exists():
        return {"roles": [], "runs": {}, "schedule": {"enabled": False}, "mode": "mock"}
    return json.loads(STATE.read_text(encoding="utf-8"))

def save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

def seed(s):
    roles = {x["id"]: x for x in s["roles"]}
    for i in range(1, 2001):
        rid = f"role-{i:04d}"
        role = roles.get(rid, {"id": rid})
        role.update({"title": ACTIVE[i-1] if i <= len(ACTIVE) else f"synthetic_specialist_{i:04d}", "active": i <= len(ACTIVE), "unit": "mock"})
        roles[rid] = role
    s["roles"] = sorted(roles.values(), key=lambda x: x["id"])
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
        n = seed(s); save(s); out = {"mode":"mock", "roles":n, "active_sample_roles":len(ACTIVE)}
    elif a.cmd == "run":
        r = run(s, a.task_id); r["evaluation"] = evaluate(r); save(s); out = r
    else: out = {"mode":s["mode"], "roles":len(s["roles"]), "runs":len(s["runs"]), "schedule":s["schedule"]}
    print(json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True))

if __name__ == "__main__": main()
