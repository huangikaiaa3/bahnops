import asyncio
from datetime import datetime

from api.app.ingestion import deutschebahn_api, normalize

async def poll_target_once(station_name: str, hour_offset: int = 0, time_now: datetime | None = None, ) -> dict:
    station_xml = await deutschebahn_api.lookup_station(station_name=station_name)
    station_eva_number = normalize.parse_station_eva_number(station_xml)

    plan_xml, fchg_xml = await asyncio.gather(
        deutschebahn_api.fetch_plan(
            eva_number=station_eva_number,
            hour_offset=hour_offset,
            time_now=time_now,
        ),
        deutschebahn_api.fetch_fchg(eva_number=station_eva_number),
    )

    normalized_target_snapshot = normalize.normalize_station_snapshot(station_name=station_name, station_xml=station_xml, plan_xml=plan_xml, fchg_xml=fchg_xml,)

    return normalized_target_snapshot