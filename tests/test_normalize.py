import json
from pathlib import Path
import unittest

from api.app.ingestion.normalize import normalize_station_snapshot


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "normalize"


def read_fixture(filename: str) -> str:
    return (FIXTURES_DIR / filename).read_text(encoding="utf-8")


class NormalizeStationSnapshotTests(unittest.TestCase):
    def test_normalize_station_snapshot_matches_expected_output(self) -> None:
        station_xml = read_fixture("station.xml")
        plan_xml = read_fixture("plan.xml")
        fchg_xml = read_fixture("fchg.xml")
        expected_snapshot = json.loads(
            read_fixture("expected_station_snapshot.json")
        )

        snapshot = normalize_station_snapshot(
            station_xml=station_xml,
            plan_xml=plan_xml,
            fchg_xml=fchg_xml,
        )

        snapshot.pop("captured_at", None)

        self.assertEqual(snapshot, expected_snapshot)


if __name__ == "__main__":
    unittest.main()
