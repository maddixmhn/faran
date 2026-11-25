import hashlib
import json
from pathlib import Path
import unittest

from check_seat_race import CHECKS, MAX_BYTES, review


ARCHIVE = Path(__file__).resolve().parents[2] / "infra/workflow/data/semester/public/seat-race.json"


class SeatRaceReview(unittest.TestCase):
    def setUp(self):
        self.source = ARCHIVE.read_bytes()
        self.data = json.loads(self.source)

    def statuses(self):
        report = review(json.dumps(self.data).encode())
        return tuple(report["checks"][key]["status"] for key in CHECKS)

    def test_archive_with_digest(self):
        report = review(self.source)
        self.assertEqual(report["sha256"], hashlib.sha256(self.source).hexdigest())
        self.assertEqual(self.statuses(), ("pass", "pass", "pass"))
        self.assertEqual(list(report["checks"]["traceable-requests"]["evidence"]["request_executions"].values()), ["5", "6"])

    def test_source_verdict_is_not_used(self):
        self.data["verified"] = False
        self.assertEqual(self.statuses(), ("pass", "pass", "pass"))

    def test_incorrect_occupancy(self):
        self.data["occupancy"] = 2
        self.assertEqual(self.statuses(), ("fail", "pass", "pass"))

    def test_loser_lost_its_seat(self):
        self.data["requests"][1]["origin"] = False
        self.assertEqual(self.statuses(), ("pass", "fail", "pass"))

    def test_duplicate_identity(self):
        self.data["requests"][1]["execution"] = self.data["requests"][0]["execution"]
        self.assertEqual(self.statuses(), ("pass", "pass", "fail"))

    def test_missing_identity(self):
        del self.data["requests"][1]["execution"]
        self.assertEqual(self.statuses(), ("pass", "pass", "insufficient"))

    def test_no_overlap(self):
        first, second = self.data["requests"]
        second.update(ready=first["finished"] + 1, finished=first["finished"] + 2)
        self.assertEqual(self.statuses(), ("pass", "pass", "fail"))

    def test_incomplete_membership(self):
        del self.data["requests"][1]["origin"]
        self.assertEqual(self.statuses(), ("insufficient", "insufficient", "pass"))

    def test_invalid_json(self):
        for data in (b"not json", b'{"requests":[],"requests":[]}'):
            self.assertEqual({item["status"] for item in review(data)["checks"].values()}, {"insufficient"})

    def test_oversize(self):
        self.assertIsNone(review(b"x" * (MAX_BYTES + 1))["sha256"])
