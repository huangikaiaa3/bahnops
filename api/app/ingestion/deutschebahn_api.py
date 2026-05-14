from dotenv import load_dotenv
import os
import httpx
from datetime import datetime
from api.app.utils.time import get_fetch_plan_target_time

BASE_URL = "https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1"

ENDPOINTS = {
    "station": "/station/{station_name}",
    "plan": "/plan/{eva_number}/{date}/{hour}",
    "fchg": "/fchg/{eva_number}",
}

def _get_credentials() -> tuple[str, str]:
    load_dotenv()
    CLIENT_ID = os.getenv("DB_CLIENT_ID")
    API_KEY = os.getenv("DB_API_KEY")
    
    if not CLIENT_ID or not API_KEY:
        raise ValueError("Invalid credentials.")
    
    return CLIENT_ID, API_KEY

def _create_headers() -> dict[str, str]:
    CLIENT_ID, API_KEY = _get_credentials()
    
    return {
        "DB-Client-Id": CLIENT_ID,
        "DB-Api-Key": API_KEY,
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

    return BASE_URL + path

async def _fetch_xml(path: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(path, headers=_create_headers(),)
        response.raise_for_status()
        return response.text
    
async def lookup_station(station_name: str) -> str:
    url = _get_url(endpoint_name="station", station_name=station_name)
    station_xml = await _fetch_xml(path=url)
    
    return station_xml

async def fetch_plan(eva_number: str, hour_offset: int = 0, time_now: datetime | None = None,) -> str:
    if time_now is None:
        time_now = datetime.now()

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
