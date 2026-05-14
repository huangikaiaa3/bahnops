from pathlib import Path
import unittest
from unittest.mock import ANY, AsyncMock, patch

from api.app.ingestion.pipeline import poll_target_once, run_poll_loop, run_poll_once
from tests.constants import FIXED_TEST_TIMESTAMP


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "normalize"


def read_fixture(filename: str) -> str:
    return (FIXTURES_DIR / filename).read_text(encoding="utf-8")


class PollTargetOnceTests(unittest.IsolatedAsyncioTestCase):
    async def test_poll_target_once_returns_raw_xml_responses(self) -> None:
        station_xml = read_fixture("station.xml")
        plan_xml = read_fixture("plan.xml")
        fchg_xml = read_fixture("fchg.xml")

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
            result = await poll_target_once(
                station_name="Berlin Ostbahnhof",
                hour_offset=1,
                time_now=FIXED_TEST_TIMESTAMP,
            )

        self.assertEqual(result, (station_xml, plan_xml, fchg_xml))
        lookup_station.assert_awaited_once_with(station_name="Berlin Ostbahnhof")
        fetch_plan.assert_awaited_once_with(
            eva_number="8010255",
            hour_offset=1,
            time_now=FIXED_TEST_TIMESTAMP,
        )
        fetch_fchg.assert_awaited_once_with(eva_number="8010255")

    async def test_run_poll_once_returns_snapshot_and_persistence_result(self) -> None:
        station_xml = read_fixture("station.xml")
        plan_xml = read_fixture("plan.xml")
        fchg_xml = read_fixture("fchg.xml")
        snapshot = {
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
            new=AsyncMock(return_value=(station_xml, plan_xml, fchg_xml)),
        ) as poll_target_once_mock, patch(
            "api.app.ingestion.pipeline.normalize_poll_response",
            return_value=snapshot.copy(),
        ) as normalize_poll_response_mock, patch(
            "api.app.ingestion.pipeline.persist_poll_response",
            return_value=persistence_result,
        ) as persist_poll_response_mock:
            result = await run_poll_once(
                station_name="Berlin Ostbahnhof",
                hour_offset=1,
                time_now=FIXED_TEST_TIMESTAMP,
            )

        self.assertEqual(result["persistence"], persistence_result)
        self.assertEqual(result["snapshot"]["station"], snapshot["station"])
        self.assertEqual(result["snapshot"]["services"], snapshot["services"])
        self.assertIn("captured_at", result["snapshot"])
        poll_target_once_mock.assert_awaited_once_with(
            station_name="Berlin Ostbahnhof",
            hour_offset=1,
            time_now=FIXED_TEST_TIMESTAMP,
        )
        normalize_poll_response_mock.assert_called_once_with(
            station_xml=station_xml,
            plan_xml=plan_xml,
            fchg_xml=fchg_xml,
        )
        persist_poll_response_mock.assert_called_once_with(
            result["snapshot"],
            ANY,
            ANY,
        )


class RunPollLoopTests(unittest.IsolatedAsyncioTestCase):
    async def test_run_poll_loop_stops_after_max_runs_without_extra_sleep(self) -> None:
        result = {
            "snapshot": {
                "station": {
                    "name": "Berlin Ostbahnhof",
                    "eva_number": "8010255",
                },
                "services": [],
                "captured_at": "2026-05-14T12:00:00+02:00",
            },
            "persistence": {
                "success": True,
                "eva_number": "8010255",
            },
        }

        with patch(
            "api.app.ingestion.pipeline.run_poll_once",
            new=AsyncMock(return_value=result),
        ) as run_poll_once_mock, patch(
            "api.app.ingestion.pipeline.asyncio.sleep",
            new=AsyncMock(),
        ) as sleep_mock, patch("builtins.print") as print_mock:
            await run_poll_loop(
                station_names=["Berlin Ostbahnhof"],
                poll_interval_seconds=180,
                max_runs=1,
            )

        run_poll_once_mock.assert_awaited_once_with(
            station_name="Berlin Ostbahnhof",
            hour_offset=0,
        )
        sleep_mock.assert_not_awaited()
        print_mock.assert_called_once_with(
            "Poll persisted successfully for EVA 8010255"
        )


if __name__ == "__main__":
    unittest.main()
