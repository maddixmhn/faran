"""Run one synthetic enrolment locally. Report native service times and dispatcher handoffs."""
import datetime as dt
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
BASE = "http://localhost:3100/api"
N8N = "faran-workflow-n8n-1"
LMS = "faran-lms-lms-1"


def api(path, body=None):
    data = json.dumps(body).encode() if body else None
    request = urllib.request.Request(BASE + path, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=12) as response:
        return json.load(response)


def docker(*args):
    return subprocess.check_output(["docker", *args], encoding="utf-8", errors="replace", timeout=150)


def millis(stamp):
    return round(dt.datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()*1000)


def now():
    return time.time_ns() // 1000000


def main():
    template = json.loads((ROOT/"workflows/faran-semester.local.json").read_text(encoding="utf-8-sig"))
    start, plan, choose = template["nodes"][:3]
    choose["parameters"]["jsCode"] = """const p = $input.first().json;
if (!p.pm.run || !p.cto.majors.length || p.pm.students !== 100) throw Error('Invalid academic plan');
return [{json:{trace:p.pm.run, major:p.cto.majors[0], execution:String($execution.id)}}];"""
    template.update(id="FaranTraceEnroll01", name="فاران | ثبت‌نام آزمایشی با رهگیری", nodes=[start,plan,choose],
                    connections={k:template["connections"][k] for k in (start["name"],plan["name"])})
    with tempfile.TemporaryDirectory() as folder:
        workflow = Path(folder)/"workflow.json"
        workflow.write_text(json.dumps(template), encoding="utf-8")
        docker("cp", str(workflow), N8N+":/tmp/faran-trace.json")
        docker("exec", N8N,"n8n","import:workflow","--input=/tmp/faran-trace.json")
        docker("cp",str(ROOT/"scripts/trace-enrol.php"), LMS+":/tmp/faran-trace.php")
        run = api("/agents/8fd3ada9-5193-4ecf-b903-13c88840796d/wakeup",
                  {"source":"on_demand","triggerDetail":"manual","reason":"Trace one synthetic Moodle registration"})
        trace = str(uuid.UUID(run["id"]))
        for _ in range(100):
            run = api("/heartbeat-runs/"+trace)
            if run.get("finishedAt"):
                break
            time.sleep(.25)
        if run.get("status") != "succeeded":
            raise RuntimeError("Manager did not complete: "+str(run.get("status")))
        dispatched = now()
        raw = docker("exec","-e","N8N_RUNNERS_BROKER_PORT=5689",N8N,"n8n","execute","--id=FaranTraceEnroll01","--rawOutput")
        execution = json.JSONDecoder().raw_decode(raw[raw.index("\n{")+1:])[0]
        nodes = execution["data"]["resultData"]["runData"]
        records = [items[0] for items in nodes.values()]
        output = nodes[choose["name"]][0]["data"]["main"][0][0]["json"]
        if output["trace"] != trace:
            raise RuntimeError("The semester plan belongs to a different manager run")
        handed = now()
        enrol = json.loads(docker("exec",LMS,"php","/tmp/faran-trace.php",trace,output["major"]))
        if enrol["trace"] != trace or not enrol["verified"]:
            raise RuntimeError("Moodle membership verification failed")
        stages = [
            ["Paperclip",millis(run["createdAt"]),millis(run["startedAt"]),millis(run["finishedAt"])],
            ["n8n",dispatched,min(r["startTime"] for r in records),max(r["startTime"]+r["executionTime"] for r in records)],
            ["Moodle",handed,enrol["start"],enrol["end"]]]
        report = {"task_id":trace,"n8n_execution":output["execution"],"moodle_course":enrol["course"],
                  "verified":True,"stages":[]}
        for name,submitted,start_ms,end in stages:
            if not submitted <= start_ms <= end:
                raise RuntimeError("Clock order invalid for "+name)
            report["stages"].append(dict(name=name,submitted=submitted,started=start_ms,ended=end,
                                         wait_ms=start_ms-submitted,service_ms=end-start_ms))
        print(json.dumps(report))
        target=ROOT/"data/semester/public/registration-trace.json"
        temp=target.with_suffix(".tmp")
        temp.write_text(json.dumps(report),encoding="utf-8")
        os.replace(temp,target)


if __name__ == "__main__":
    main()
