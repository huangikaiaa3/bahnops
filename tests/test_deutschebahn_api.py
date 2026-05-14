import httpx
import unittest
from unittest.mock import AsyncMock, Mock, patch

from api.app.ingestion.deutschebahn_api import _fetch_xml, fetch_plan
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

    async def test_fetch_xml_uses_configured_timeout(self) -> None:
        response = Mock()
        response.text = "<station />"
        response.raise_for_status.return_value = None

        client = AsyncMock()
        client.get.return_value = response

        client_context = AsyncMock()
        client_context.__aenter__.return_value = client
        client_context.__aexit__.return_value = None

        with patch(
            "api.app.ingestion.deutschebahn_api.config.db_request_timeout_seconds",
            "10",
        ), patch(
            "api.app.ingestion.deutschebahn_api.config.db_request_retry_count",
            "2",
        ), patch(
            "api.app.ingestion.deutschebahn_api.config.db_request_retry_delay_seconds",
            "2",
        ), patch(
            "api.app.ingestion.deutschebahn_api.httpx.AsyncClient",
            return_value=client_context,
        ) as async_client:
            xml = await _fetch_xml("https://example.com/test.xml")

        self.assertEqual(xml, "<station />")
        async_client.assert_called_once_with(timeout=10.0)
        client.get.assert_awaited_once()

    async def test_fetch_xml_retries_after_http_error_and_then_succeeds(self) -> None:
        response = Mock()
        response.text = "<station />"
        response.raise_for_status.return_value = None

        client = AsyncMock()
        client.get.side_effect = [
            httpx.HTTPError("temporary failure"),
            response,
        ]

        client_context = AsyncMock()
        client_context.__aenter__.return_value = client
        client_context.__aexit__.return_value = None

        with patch(
            "api.app.ingestion.deutschebahn_api.config.db_request_timeout_seconds",
            "10",
        ), patch(
            "api.app.ingestion.deutschebahn_api.config.db_request_retry_count",
            "2",
        ), patch(
            "api.app.ingestion.deutschebahn_api.config.db_request_retry_delay_seconds",
            "2",
        ), patch(
            "api.app.ingestion.deutschebahn_api.httpx.AsyncClient",
            return_value=client_context,
        ), patch(
            "api.app.ingestion.deutschebahn_api.asyncio.sleep",
            new=AsyncMock(),
        ) as sleep:
            xml = await _fetch_xml("https://example.com/test.xml")

        self.assertEqual(xml, "<station />")
        self.assertEqual(client.get.await_count, 2)
        sleep.assert_awaited_once_with(2.0)

    async def test_fetch_xml_raises_after_exhausting_retries(self) -> None:
        client = AsyncMock()
        client.get.side_effect = httpx.HTTPError("persistent failure")

        client_context = AsyncMock()
        client_context.__aenter__.return_value = client
        client_context.__aexit__.return_value = None

        with patch(
            "api.app.ingestion.deutschebahn_api.config.db_request_timeout_seconds",
            "10",
        ), patch(
            "api.app.ingestion.deutschebahn_api.config.db_request_retry_count",
            "2",
        ), patch(
            "api.app.ingestion.deutschebahn_api.config.db_request_retry_delay_seconds",
            "2",
        ), patch(
            "api.app.ingestion.deutschebahn_api.httpx.AsyncClient",
            return_value=client_context,
        ), patch(
            "api.app.ingestion.deutschebahn_api.asyncio.sleep",
            new=AsyncMock(),
        ) as sleep:
            with self.assertRaises(httpx.HTTPError):
                await _fetch_xml("https://example.com/test.xml")

        self.assertEqual(client.get.await_count, 3)
        self.assertEqual(sleep.await_count, 2)


if __name__ == "__main__":
    unittest.main()
