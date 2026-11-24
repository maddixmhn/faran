"""Replay a public synthetic semester against the separate evaluator implementation."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import json
import subprocess

DOCS = Path(__file__).resolve().parents[1] / "docs"

def injected(source, kind):
    log = deepcopy(source)
    events = log["events"]
    graduation = next(e for e in events if e["activity"] == "graduated")
    if kind == "early-graduation":
        events.remove(graduation)
        position = next(i for i,e in enumerate(events) if e["activity"] == "appeal_opened")+1
        graduation["minute"] = events[position-1]["minute"]
        events.insert(position,graduation)
    if kind == "no-clearance":
        events[:] = [e for e in events if e["activity"] != "clearance_verified"]
    if kind == "repeated-enrolment":
        index = next(i for i,e in enumerate(events) if e["activity"] == "enrolled")
        events.insert(index+1,{**events[index],"event_id":"duplicate-seat-test"})
    if kind == "capacity-one":
        log["capacity"]["seminar-demo"] = 1
    if kind == "duplicate-id":
        events.insert(1,dict(events[0]))
    if kind == "clock-regression":
        events[-1]["minute"] = -1
    return log

def main():
    args = argparse.ArgumentParser()
    args.add_argument("evaluator",type=Path)
    engine = args.parse_args().evaluator.resolve(strict=True)
    original = json.loads((DOCS / "semester-web.json").read_text(encoding="utf8"))
    expected = {
        "baseline":None, "early-graduation":"OPEN_APPEAL", "no-clearance":"DEGREE_EVIDENCE",
        "repeated-enrolment":"DUPLICATE_SEAT", "capacity-one":"CAPACITY",
        "duplicate-id":"invalid-input", "clock-regression":"invalid-input",
    }
    summary = []
    with TemporaryDirectory() as temp:
        fixture = Path(temp) / "journey.json"
        for name, rule in expected.items():
            fixture.write_text(json.dumps(injected(original,name),ensure_ascii=False),encoding="utf8")
            run = subprocess.run(["node",str(engine),str(fixture)],capture_output=True,encoding="utf8",check=False)
            if rule == "invalid-input":
                assert run.returncode != 0 and "Invalid event identity, capacity or clock" in run.stderr, name
                findings = []
                status = "invalid-input"
            else:
                run.check_returncode()
                data = json.loads(run.stdout)
                findings = [{"rule":f["rule"],"event":f["event_id"]} for f in data["findings"]]
                if rule is None:
                    assert not findings and [w["minutes"] for w in data["observedWaits"]]==[9], name
                else:
                    assert any(f["rule"] == rule for f in findings), name
                status = "audit-complete"
            summary.append({"scenario":name,"status":status,"findings":findings})
    evidence_file = DOCS / "seminar-results.json"
    evidence = json.loads(evidence_file.read_text(encoding="utf8"))
    evidence["replay_checks"] = summary
    evidence_file.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("Verified",len(summary),"evaluator replay cases")

if __name__=="__main__":
    main()
