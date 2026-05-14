import unittest
from unittest.mock import AsyncMock, patch

from api.app.ingestion.deutschebahn_api import fetch_plan
from tests.constants import FIXED_TEST_TIMESTAMP


class FetchPlanTests(unittest.IsolatedAsyncioTestCase):
    async def test_fetch_plan_uses_fixed_timestamp_when_provided(self) -> None:
        with patch(
            "api.app.ingestion.deutschebahn_api._fetch_xml",
            new=AsyncMock(return_value="<timetable />"),
        ) as fetch_xml:
            await fetch_plan(
                eva_number="8010255",
                hour_offset=1,
                time_now=FIXED_TEST_TIMESTAMP,
            )

        fetch_xml.assert_awaited_once_with(
            path=(
                "https://apis.deutschebahn.com/db-api-marketplace/apis/"
                "timetables/v1/plan/8010255/260514/11"
            )
        )


if __name__ == "__main__":
    unittest.main()
