import json
from pathlib import Path
import unittest
from unittest.mock import AsyncMock, patch

from api.app.ingestion.pipeline import poll_target_once
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


if __name__ == "__main__":
    unittest.main()
