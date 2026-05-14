from datetime import datetime
import json
from pathlib import Path
import unittest

from api.app.ingestion.persistence import (
    get_poll_run_data,
    get_service_data,
    get_service_state_current_data,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "normalize"


def read_fixture(filename: str) -> str:
    return (FIXTURES_DIR / filename).read_text(encoding="utf-8")


class PersistenceMappingTests(unittest.TestCase):
    def test_get_poll_run_data_uses_passed_timestamps(self) -> None:
        snapshot = {"services": [{} for _ in range(3)]}
        started_at = datetime.fromisoformat("2026-05-14T12:00:00+02:00")
        finished_at = datetime.fromisoformat("2026-05-14T12:00:04+02:00")

        poll_run_data = get_poll_run_data(
            poll_target_id=1,
            snapshot=snapshot,
            started_at=started_at,
            finished_at=finished_at,
        )

        self.assertEqual(poll_run_data["poll_target_id"], 1)
        self.assertEqual(poll_run_data["started_at"], started_at)
        self.assertEqual(poll_run_data["finished_at"], finished_at)
        self.assertEqual(poll_run_data["services_seen"], 3)
        self.assertEqual(poll_run_data["status"], "success")

    def test_get_service_data_builds_expected_observation_rows(self) -> None:
        snapshot = json.loads(read_fixture("expected_station_snapshot.json"))
        snapshot["captured_at"] = "2026-05-14T12:00:00+02:00"

        service_data = get_service_data(snapshot)

        self.assertEqual(set(service_data.keys()), {"srv-1-1", "srv-2-1"})

        first_service = service_data["srv-1-1"]
        self.assertEqual(first_service["service_run_uid"], "srv-1")
        self.assertEqual(first_service["stop_sequence"], 1)
        self.assertEqual(first_service["observed_at"], "2026-05-14T12:00:00+02:00")
        self.assertEqual(
            json.loads(first_service["planned_arrival_path"]),
            ["Leipzig", "Berlin Hbf"],
        )
        self.assertEqual(
            json.loads(first_service["current_departure_path"]),
            ["Berlin Hbf", "Spandau"],
        )

    def test_get_service_state_current_data_falls_back_to_planned_values(self) -> None:
        service_observation_data = {
            "srv-2-1": {
                "service_id": 2,
                "poll_run_id": 10,
                "observed_at": "2026-05-14T12:00:00+02:00",
                "planned_arrival": None,
                "current_arrival": None,
                "planned_departure": "2605141230",
                "current_departure": None,
                "planned_arrival_platform": None,
                "current_arrival_platform": None,
                "planned_departure_platform": "2",
                "current_departure_platform": None,
            }
        }

        current_state_data = get_service_state_current_data(service_observation_data)

        self.assertEqual(
            current_state_data["srv-2-1"]["current_departure"],
            "2605141230",
        )
        self.assertEqual(
            current_state_data["srv-2-1"]["current_departure_platform"],
            "2",
        )
        self.assertFalse(current_state_data["srv-2-1"]["is_cancelled"])


if __name__ == "__main__":
    unittest.main()
