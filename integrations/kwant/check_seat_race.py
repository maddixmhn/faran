"""Read archived Faran seat-race evidence and calculate each acceptance check."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import re


CHECKS = ("single-transfer", "origin-preserved", "traceable-requests")
MEMBERSHIP = ("moved", "origin", "target")
MAX_BYTES = 65_536


def verdict(status, detail, **evidence):
    return {"status": status, "detail": detail, "evidence": evidence}


def link_requests(race, rows):
    required = ("request_id", "execution", "ready", "finished")
    if race is None or any(field not in row for row in rows for field in required):
        return verdict("insufficient", "Race identity, execution identity or timing is missing.")
    ids = [row["request_id"] for row in rows]
    executions = [row["execution"] for row in rows]
    if not isinstance(race, str) or re.fullmatch(r"[0-9a-f]{32}", race) is None:
        return verdict("fail", "Race identity is invalid.")
    if not all(isinstance(value, str) for value in ids) or set(ids) != {race + "-0", race + "-1"}:
        return verdict("fail", "Request identities do not uniquely identify both entries in the race.")
    if not all(isinstance(value, str) and re.fullmatch(r"[1-9][0-9]*", value) for value in executions):
        return verdict("fail", "An n8n execution identity is invalid.")
    if executions[0] == executions[1]:
        return verdict("fail", "The two requests point to the same execution.")
    timestamps = [row[field] for row in rows for field in ("ready", "finished")]
    if not all(type(value) in (int, float) and 0 <= value <= 10**12 and math.isfinite(value) for value in timestamps):
        return verdict("fail", "An invalid timestamp prevents ordering.")
    if any(row["ready"] >= row["finished"] for row in rows):
        return verdict("fail", "A request finished before or at its observed ready time.")
    overlap = min(row["finished"] for row in rows) - max(row["ready"] for row in rows)
    if overlap <= 0:
        return verdict("fail", "The two observed time intervals do not overlap.")
    return verdict("pass", "Both requests link to distinct executions with overlapping observed intervals.",
                   request_executions=dict(zip(ids, executions, strict=True)), overlap_ms=round(overlap * 1000, 3))


def review_membership(rows, occupancy):
    if any(field not in row for row in rows for field in MEMBERSHIP):
        unavailable = verdict("insufficient", "Membership evidence is missing.")
        return unavailable, unavailable
    if any(type(row[field]) is not bool for row in rows for field in MEMBERSHIP):
        invalid = verdict("fail", "Membership flags must be boolean.")
        return invalid, invalid
    winners = [row for row in rows if row["moved"]]
    losers = [row for row in rows if not row["moved"]]
    losing_rows_preserved = len(losers) == 1 and losers[0]["origin"] and not losers[0]["target"]
    original = verdict("pass" if losing_rows_preserved else "fail",
                       "One losing request must keep its original membership only.")
    if occupancy is None:
        return verdict("insufficient", "Final destination occupancy is missing."), original
    if type(occupancy) is not int:
        return verdict("fail", "Final destination occupancy must be an integer."), original
    target_count = sum(row["target"] for row in rows)
    valid = occupancy == target_count == len(winners) == 1
    valid = valid and winners[0]["target"] and not winners[0]["origin"]
    transfer = verdict("pass" if valid else "fail", "One consistent transfer must occupy the last seat.",
                       moved_count=len(winners), final_occupancy=occupancy, observed_targets=target_count)
    return transfer, original


def unique_keys(items):
    result = dict(items)
    if len(result) != len(items):
        raise ValueError("Duplicate JSON key")
    return result


def review(source):
    if len(source) > MAX_BYTES:
        return {"sha256": None, "checks": {key: verdict("insufficient", "Evidence is too large.") for key in CHECKS}}
    digest = hashlib.sha256(source).hexdigest()
    try:
        data = json.loads(source, object_pairs_hook=unique_keys)
    except (ValueError, RecursionError):
        data = None
    rows = data.get("requests") if isinstance(data, dict) else None
    if not isinstance(rows, list) or len(rows) != 2 or not all(isinstance(row, dict) for row in rows):
        missing = verdict("insufficient", "Exactly two request records are required.")
        return {"sha256": digest, "checks": dict.fromkeys(CHECKS, missing)}
    transfer, origin = review_membership(rows, data.get("occupancy"))
    trace = link_requests(data.get("race"), rows)
    return {"sha256": digest, "checks": dict(zip(CHECKS, (transfer, origin, trace), strict=True))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    parser.add_argument("--check", choices=CHECKS)
    args = parser.parse_args()
    with args.path.open("rb") as stream:
        result = review(stream.read(MAX_BYTES + 1))
    if args.check:
        result["checks"] = {args.check: result["checks"][args.check]}
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0 if all(item["status"] == "pass" for item in result["checks"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
