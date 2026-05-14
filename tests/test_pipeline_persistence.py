import unittest
from unittest.mock import patch

from api.app.ingestion.pipeline import persist_poll_response


class PersistPollResponseTests(unittest.TestCase):
    def test_persist_poll_response_writes_snapshot_with_configured_database_url(self) -> None:
        snapshot = {
            "captured_at": "2026-05-14T12:00:00+02:00",
            "station": {
                "name": "Berlin Ostbahnhof",
                "eva_number": "8010255",
            },
            "services": [],
        }

        with patch(
            "api.app.ingestion.pipeline.config.database_url",
            "postgresql://bahnops:test@localhost:5432/bahnops",
        ), patch(
            "api.app.ingestion.pipeline.persistence.write_snapshot_to_db"
        ) as write_snapshot_to_db:
            response = persist_poll_response(snapshot)

        write_snapshot_to_db.assert_called_once_with(
            database_url="postgresql://bahnops:test@localhost:5432/bahnops",
            snapshot=snapshot,
        )
        self.assertEqual(
            response,
            {
                "success": True,
                "eva_number": "8010255",
            },
        )

    def test_persist_poll_response_requires_database_url(self) -> None:
        with patch("api.app.ingestion.pipeline.config.database_url", None):
            with self.assertRaisesRegex(ValueError, "DATABASE_URL is not set"):
                persist_poll_response({})


if __name__ == "__main__":
    unittest.main()
