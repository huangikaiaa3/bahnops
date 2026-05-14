from datetime import datetime, timezone
import unittest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from api.app.core.exceptions import ServiceNotFoundError, StationNotFoundError
from api.app.db.session import get_db_connection
from api.app.main import app


async def override_db_connection():
    yield object()


def as_api_datetime(value: datetime) -> str:
    return value.isoformat().replace("+00:00", "Z")


class ApiReadTests(unittest.TestCase):
    def setUp(self) -> None:
        app.dependency_overrides[get_db_connection] = override_db_connection
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()
        self.client.close()

    def test_health_returns_ok(self) -> None:
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_station_services_returns_services(self) -> None:
        last_seen_at = datetime(2026, 5, 14, 12, 0, tzinfo=timezone.utc)
        mocked_services = [
            {
                "service_id": 1,
                "display_name": "ICE 100",
                "category": "ICE",
                "number": "100",
                "line": "ICE 100",
                "planned_arrival": None,
                "current_arrival": None,
                "planned_departure": datetime(2026, 5, 14, 12, 5, tzinfo=timezone.utc),
                "current_departure": datetime(2026, 5, 14, 12, 8, tzinfo=timezone.utc),
                "planned_arrival_platform": None,
                "current_arrival_platform": None,
                "planned_departure_platform": "7",
                "current_departure_platform": "8",
                "is_cancelled": False,
                "last_seen_at": last_seen_at,
            }
        ]

        with patch(
            "api.app.routes.stations.get_station_services_response",
            new=AsyncMock(return_value=mocked_services),
        ) as get_station_services_response:
            response = self.client.get("/stations/8010255/services")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["service_id"], 1)
        self.assertEqual(body[0]["display_name"], "ICE 100")
        self.assertEqual(body[0]["planned_departure_platform"], "7")
        self.assertEqual(body[0]["current_departure_platform"], "8")
        self.assertEqual(body[0]["last_seen_at"], as_api_datetime(last_seen_at))
        get_station_services_response.assert_awaited_once()

    def test_station_services_returns_404_when_station_not_found(self) -> None:
        with patch(
            "api.app.routes.stations.get_station_services_response",
            new=AsyncMock(side_effect=StationNotFoundError),
        ):
            response = self.client.get("/stations/9999999/services")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Station not found"})

    def test_service_detail_returns_service(self) -> None:
        last_seen_at = datetime(2026, 5, 14, 12, 0, tzinfo=timezone.utc)
        mocked_service = {
            "service_id": 1,
            "service_run_uid": "srv-1",
            "display_name": "ICE 100",
            "category": "ICE",
            "number": "100",
            "line": "ICE 100",
            "planned_arrival": None,
            "current_arrival": None,
            "planned_departure": datetime(2026, 5, 14, 12, 5, tzinfo=timezone.utc),
            "current_departure": datetime(2026, 5, 14, 12, 8, tzinfo=timezone.utc),
            "planned_arrival_platform": None,
            "current_arrival_platform": None,
            "planned_departure_platform": "7",
            "current_departure_platform": "8",
            "is_cancelled": False,
            "last_seen_at": last_seen_at,
        }

        with patch(
            "api.app.routes.services.get_service_detail_response",
            new=AsyncMock(return_value=mocked_service),
        ) as get_service_detail_response:
            response = self.client.get("/services/1")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["service_id"], 1)
        self.assertEqual(body["service_run_uid"], "srv-1")
        self.assertEqual(body["current_departure_platform"], "8")
        self.assertEqual(body["last_seen_at"], as_api_datetime(last_seen_at))
        get_service_detail_response.assert_awaited_once()

    def test_service_detail_returns_404_when_service_not_found(self) -> None:
        with patch(
            "api.app.routes.services.get_service_detail_response",
            new=AsyncMock(side_effect=ServiceNotFoundError),
        ):
            response = self.client.get("/services/999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Service not found"})

    def test_service_changes_returns_changes(self) -> None:
        event_time = datetime(2026, 5, 14, 12, 8, tzinfo=timezone.utc)
        mocked_changes = [
            {
                "service_id": 1,
                "poll_run_id": 5,
                "event_time": event_time,
                "event_type": "current_departure_changed",
                "old_value": "2605141205",
                "new_value": "2605141208",
            }
        ]

        with patch(
            "api.app.routes.services.get_service_changes_response",
            new=AsyncMock(return_value=mocked_changes),
        ) as get_service_changes_response:
            response = self.client.get("/services/1/changes")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["service_id"], 1)
        self.assertEqual(body[0]["event_type"], "current_departure_changed")
        self.assertEqual(body[0]["event_time"], as_api_datetime(event_time))
        get_service_changes_response.assert_awaited_once()

    def test_service_changes_returns_404_when_service_not_found(self) -> None:
        with patch(
            "api.app.routes.services.get_service_changes_response",
            new=AsyncMock(side_effect=ServiceNotFoundError),
        ):
            response = self.client.get("/services/999/changes")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Service not found"})

    def test_targets_returns_targets(self) -> None:
        mocked_targets = [
            {
                "id": 1,
                "station_id": 10,
                "station_eva_number": "8010255",
                "station_name": "Berlin Ostbahnhof",
                "target_type": "station_board",
                "poll_interval_seconds": 180,
                "is_active": True,
            }
        ]

        with patch(
            "api.app.routes.targets.get_targets",
            new=AsyncMock(return_value=mocked_targets),
        ) as get_targets:
            response = self.client.get("/targets")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), mocked_targets)
        get_targets.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
