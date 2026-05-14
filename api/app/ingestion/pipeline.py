import asyncio
from datetime import datetime

from api.app.core.config import config
from api.app.ingestion import deutschebahn_api, normalize, persistence


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

    return normalize.normalize_station_snapshot(station_xml=station_xml, plan_xml=plan_xml, fchg_xml=fchg_xml)


def normalize_poll_response(station_xml: str, plan_xml: str, fchg_xml: str) -> dict:
    return normalize.normalize_station_snapshot(station_xml=station_xml, plan_xml=plan_xml, fchg_xml=fchg_xml,)

def persist_poll_response(normalized_response: dict) -> dict:
    if not config.database_url:
        raise ValueError("DATABASE_URL is not set")

    persistence.write_snapshot_to_db(
        database_url=config.database_url,
        snapshot=normalized_response,
    )

    return {
        "success": True,
        "eva_number": normalized_response["station"]["eva_number"],
    }


async def run_poll_once(station_name: str, hour_offset: int = 0, time_now: datetime | None = None,) -> dict:
    normalized_response = await poll_target_once(
        station_name=station_name,
        hour_offset=hour_offset,
        time_now=time_now,
    )
    persistence_response = persist_poll_response(normalized_response)

    return {
        "snapshot": normalized_response,
        "persistence": persistence_response,
    }
