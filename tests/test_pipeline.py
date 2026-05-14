import json
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, patch

from api.app.ingestion.pipeline import poll_target_once, run_poll_once
from tests.constants import FIXED_TEST_TIMESTAMP


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "normalize"


def read_fixture(filename: str) -> str:
    return (FIXTURES_DIR / filename).read_text(encoding="utf-8")


class PollTargetOnceTests(unittest.IsolatedAsyncioTestCase):
    async def test_poll_target_once_returns_expected_snapshot(self) -> None:
        station_xml = read_fixture("station.xml")
        plan_xml = read_fixture("plan.xml")
        fchg_xml = read_fixture("fchg.xml")
        expected_snapshot = json.loads(
            read_fixture("expected_station_snapshot.json")
        )

        with patch(
            "api.app.ingestion.pipeline.deutschebahn_api.lookup_station",
            new=AsyncMock(return_value=station_xml),
        ) as lookup_station, patch(
            "api.app.ingestion.pipeline.deutschebahn_api.fetch_plan",
            new=AsyncMock(return_value=plan_xml),
        ) as fetch_plan, patch(
            "api.app.ingestion.pipeline.deutschebahn_api.fetch_fchg",
            new=AsyncMock(return_value=fchg_xml),
        ) as fetch_fchg:
            snapshot = await poll_target_once(
                station_name="Berlin Ostbahnhof",
                hour_offset=1,
                time_now=FIXED_TEST_TIMESTAMP,
            )

        snapshot.pop("captured_at", None)

        self.assertEqual(snapshot, expected_snapshot)
        lookup_station.assert_awaited_once_with(station_name="Berlin Ostbahnhof")
        fetch_plan.assert_awaited_once_with(
            eva_number="8010255",
            hour_offset=1,
            time_now=FIXED_TEST_TIMESTAMP,
        )
        fetch_fchg.assert_awaited_once_with(eva_number="8010255")

    async def test_run_poll_once_returns_snapshot_and_persistence_result(self) -> None:
        snapshot = {
            "captured_at": "2026-05-14T12:00:00+02:00",
            "station": {
                "name": "Berlin Ostbahnhof",
                "eva_number": "8010255",
            },
            "services": [],
        }
        persistence_result = {
            "success": True,
            "eva_number": "8010255",
        }

        with patch(
            "api.app.ingestion.pipeline.poll_target_once",
            new=AsyncMock(return_value=snapshot),
        ) as poll_target_once_mock, patch(
            "api.app.ingestion.pipeline.persist_poll_response",
            return_value=persistence_result,
        ) as persist_poll_response_mock:
            result = await run_poll_once(
                station_name="Berlin Ostbahnhof",
                hour_offset=1,
                time_now=FIXED_TEST_TIMESTAMP,
            )

        self.assertEqual(
            result,
            {
                "snapshot": snapshot,
                "persistence": persistence_result,
            },
        )
        poll_target_once_mock.assert_awaited_once_with(
            station_name="Berlin Ostbahnhof",
            hour_offset=1,
            time_now=FIXED_TEST_TIMESTAMP,
        )
        persist_poll_response_mock.assert_called_once_with(snapshot)


if __name__ == "__main__":
    unittest.main()
