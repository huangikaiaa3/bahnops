import asyncio
import httpx
from datetime import datetime
from api.app.core.config import config
from api.app.utils.time import DB_TIMETABLE_TIMEZONE, get_fetch_plan_target_time

ENDPOINTS = {
    "station": "/station/{station_name}",
    "plan": "/plan/{eva_number}/{date}/{hour}",
    "fchg": "/fchg/{eva_number}",
}

def _get_request_timeout_seconds() -> float:
    timeout_seconds = config.db_request_timeout_seconds
    
    if not timeout_seconds:
        raise ValueError("DB API timeout seconds not found.")
    
    return float(timeout_seconds)

def _get_request_retry_count() -> int:
    retry_count = config.db_request_retry_count

    if not retry_count:
        raise ValueError("DB API retry count not found.")

    return int(retry_count)

def _get_request_retry_delay_seconds() -> float:
    retry_delay_seconds = config.db_request_retry_delay_seconds

    if not retry_delay_seconds:
        raise ValueError("DB API retry delay seconds not found.")

    return float(retry_delay_seconds)

def _get_credentials() -> tuple[str, str]:
    client_id = config.db_client_id
    api_key = config.db_api_key
    
    if not client_id or not api_key:
        raise ValueError("Invalid credentials.")
    
    return client_id, api_key

def _create_headers() -> dict[str, str]:
    client_id, api_key = _get_credentials()
    
    return {
        "DB-Client-Id": client_id,
        "DB-Api-Key": api_key,
        "Accept": "application/xml",
    }
    
def _get_url(endpoint_name: str, **params: str) -> str:
    if endpoint_name not in ENDPOINTS:
        raise ValueError(f"Invalid endpoint name: {endpoint_name}")

    path_template = ENDPOINTS[endpoint_name]

    try:
        path = path_template.format(**params)
    except KeyError as exc:
        raise ValueError(
            f"Missing parameter for endpoint '{endpoint_name}': {exc.args[0]}"
        ) from exc

    if not config.db_timetable_base_url:
        raise ValueError("DB_TIMETABLE_BASE_URL is not set")

    return config.db_timetable_base_url + path

async def _fetch_xml(path: str) -> str:
    timeout = _get_request_timeout_seconds()
    retry_count = _get_request_retry_count()
    retry_delay_seconds = _get_request_retry_delay_seconds()

    for attempt in range(retry_count + 1):
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(path, headers=_create_headers(),)
                response.raise_for_status()
                return response.text
        except httpx.HTTPError:
            if attempt == retry_count:
                raise
            await asyncio.sleep(retry_delay_seconds)
    
async def lookup_station(station_name: str) -> str:
    url = _get_url(endpoint_name="station", station_name=station_name)
    station_xml = await _fetch_xml(path=url)
    
    return station_xml

async def fetch_plan(eva_number: str, hour_offset: int = 0, time_now: datetime | None = None,) -> str:
    if time_now is None:
        time_now = datetime.now(DB_TIMETABLE_TIMEZONE)

    target_date, target_hour = get_fetch_plan_target_time(
        time_now=time_now,
        hour_offset=hour_offset,
    )
    url = _get_url(endpoint_name="plan", eva_number=eva_number, date=target_date, hour=target_hour)
    plan_xml = await _fetch_xml(path=url)
    
    return plan_xml

async def fetch_fchg(eva_number: str) -> str:
    url = _get_url(endpoint_name="fchg", eva_number=eva_number)
    fchg_xml = await _fetch_xml(path=url)
    
    return fchg_xml
