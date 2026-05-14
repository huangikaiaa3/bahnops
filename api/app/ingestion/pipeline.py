import asyncio
from datetime import datetime

from api.app.core.config import config
from api.app.ingestion import deutschebahn_api, normalize, persistence
from api.app.utils.time import DB_TIMETABLE_TIMEZONE


async def poll_target_once(station_name: str, hour_offset: int = 0, time_now: datetime | None = None, ) -> dict:
    station_xml = await deutschebahn_api.lookup_station(station_name=station_name)
    _, station_eva_number = normalize.parse_station_info(station_xml)

    plan_xml, fchg_xml = await asyncio.gather(
        deutschebahn_api.fetch_plan(
            eva_number=station_eva_number,
            hour_offset=hour_offset,
            time_now=time_now,
        ),
        deutschebahn_api.fetch_fchg(eva_number=station_eva_number),
    )

    return station_xml, plan_xml, fchg_xml


def normalize_poll_response(station_xml: str, plan_xml: str, fchg_xml: str) -> dict:
    return normalize.normalize_station_snapshot(station_xml=station_xml, plan_xml=plan_xml, fchg_xml=fchg_xml,)

def persist_poll_response(normalized_response: dict, started_at: datetime, finished_at: datetime,) -> dict:
    if not config.database_url:
        raise ValueError("DATABASE_URL is not set")

    persistence.write_snapshot_to_db(
        database_url=config.database_url,
        snapshot=normalized_response,
        started_at=started_at,
        finished_at=finished_at,
    )

    return {
        "success": True,
        "eva_number": normalized_response["station"]["eva_number"],
    }


async def run_poll_once(station_name: str, hour_offset: int = 0, time_now: datetime | None = None,) -> dict:
    started_at = datetime.now(DB_TIMETABLE_TIMEZONE)
    station_xml, plan_xml, fchg_xml = await poll_target_once(station_name=station_name, hour_offset=hour_offset, time_now=time_now,)
    finished_at = datetime.now(DB_TIMETABLE_TIMEZONE)
    
    normalized_response = normalize_poll_response(station_xml=station_xml, plan_xml=plan_xml, fchg_xml=fchg_xml)
    normalized_response["captured_at"] = finished_at.isoformat()
    persistence_response = persist_poll_response(
        normalized_response,
        started_at,
        finished_at,
    )

    return {
        "snapshot": normalized_response,
        "persistence": persistence_response,
    }


async def run_poll_loop(station_names: list[str], poll_interval_seconds: int, hour_offset: int = 0, max_runs: int | None = None,) -> None:
    if poll_interval_seconds <= 0:
        raise ValueError("poll_interval_seconds must be greater than 0")

    runs = 0
    while max_runs is None or runs < max_runs:
        results = await asyncio.gather(
            *[ run_poll_once(station_name=station_name, hour_offset=hour_offset,) for station_name in station_names ]
        )

        for result in results:
            eva_number = result["persistence"]["eva_number"]
            print(f"Poll persisted successfully for EVA {eva_number}")

        runs += 1

        if max_runs is not None and runs >= max_runs:
            break

        await asyncio.sleep(poll_interval_seconds)
