from dotenv import load_dotenv
import os
import asyncio
import httpx
import xml.etree.ElementTree as ET
import datetime
from zoneinfo import ZoneInfo
import json
from pathlib import Path

load_dotenv()

CLIENT_ID = os.getenv("DB_CLIENT_ID")
API_KEY = os.getenv("DB_API_KEY")

if not CLIENT_ID or not API_KEY:
    raise ValueError("Invalid credentials.")

BASE_URL = "https://apis.deutschebahn.com/db-api-marketplace/apis/timetables/v1"
SNAPSHOT_DIR = Path("data/snapshots")

ENDPOINTS = {
    "station": "/station/{station_name}",
    "plan": "/plan/{eva_number}/{date}/{hour}",
    "fchg": "/fchg/{eva_number}",
}

def create_headers() -> dict[str, str]:
    return {
        "DB-Client-Id": CLIENT_ID,
        "DB-Api-Key": API_KEY,
        "Accept": "application/xml",
    }

def get_url(endpoint_name: str, **params: str) -> str:
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

async def fetch_xml(path: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            path,
            headers=create_headers(),
        )
        response.raise_for_status()
        return response.text

def parse_station_eva_code(xml_str: str) -> str:
    root = ET.fromstring(xml_str)
    station = root.find("station")
    if station is None:
        raise ValueError("No station element found in station response")

    station_eva_code = station.attrib["eva"]
    return station_eva_code

def parse_fchg_updates(fchg_xml: str) -> dict[str, dict]:
    root = ET.fromstring(fchg_xml)
    updates = {}

    for service in root.findall("s"):
        service_id = service.attrib.get("id")
        if not service_id:
            continue

        ar = service.find("ar")
        dp = service.find("dp")

        current_arrival_path = []
        current_departure_path = []

        if ar is not None:
            changed_path = ar.attrib.get("cpth")
            current_arrival_path = changed_path.split("|") if changed_path else []

        if dp is not None:
            changed_path = dp.attrib.get("cpth")
            current_departure_path = changed_path.split("|") if changed_path else []

        updates[service_id] = {
            "current_arrival": ar.attrib.get("ct") if ar is not None else None,
            "current_departure": dp.attrib.get("ct") if dp is not None else None,
            "current_arrival_platform": ar.attrib.get("cp") if ar is not None else None,
            "current_departure_platform": dp.attrib.get("cp") if dp is not None else None,
            "current_arrival_path": current_arrival_path,
            "current_departure_path": current_departure_path,
        }

    return updates

def build_station_snapshot(
    plan_xml: str,
    station_name: str,
    station_eva_code: str,
    fchg_updates: dict[str, dict] | None = None,
) -> dict:
    root = ET.fromstring(plan_xml)
    captured_at = datetime.datetime.now(ZoneInfo("Europe/Berlin")).isoformat()

    services = []

    for service in root.findall("s"):
        tl = service.find("tl")
        ar = service.find("ar")
        dp = service.find("dp")

        line = None
        display_name = None

        if ar is not None:
            line = ar.attrib.get("l")
            display_name = ar.attrib.get("fb")

        if dp is not None:
            line = line or dp.attrib.get("l")
            display_name = display_name or dp.attrib.get("fb")

        planned_arrival_path = []
        planned_departure_path = []

        if ar is not None:
            planned_path = ar.attrib.get("ppth")
            planned_arrival_path = planned_path.split("|") if planned_path else []

        if dp is not None:
            planned_path = dp.attrib.get("ppth")
            planned_departure_path = planned_path.split("|") if planned_path else []

        service_id = service.attrib.get("id")
        current_update = fchg_updates.get(service_id, {}) if fchg_updates else {}

        service_data = {
            "service_id": service_id,
            "category": tl.attrib.get("c") if tl is not None else None,
            "number": tl.attrib.get("n") if tl is not None else None,
            "line": line,
            "display_name": display_name,
            "planned_arrival": ar.attrib.get("pt") if ar is not None else None,
            "planned_departure": dp.attrib.get("pt") if dp is not None else None,
            "current_arrival": current_update.get("current_arrival"),
            "current_departure": current_update.get("current_departure"),
            "planned_arrival_platform": ar.attrib.get("pp") if ar is not None else None,
            "planned_departure_platform": dp.attrib.get("pp") if dp is not None else None,
            "current_arrival_platform": current_update.get("current_arrival_platform"),
            "current_departure_platform": current_update.get("current_departure_platform"),
            "planned_arrival_path": planned_arrival_path,
            "planned_departure_path": planned_departure_path,
            "current_arrival_path": current_update.get("current_arrival_path", []),
            "current_departure_path": current_update.get("current_departure_path", []),
        }
        services.append(service_data)

    return {
        "captured_at": captured_at,
        "station": {
            "name": station_name,
            "eva_number": station_eva_code,
        },
        "services": services,
    }

def write_station_snapshot(snapshot: dict) -> Path:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = SNAPSHOT_DIR / "station_snapshot.json"
    output_path.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return output_path
    
def get_target_time(hour_offset: int = 0) -> tuple[str, str]:
    target_datetime = datetime.datetime.now() - datetime.timedelta(hours=hour_offset)
    target_date = str(target_datetime.year)[2:] + str(target_datetime.month).zfill(2) + str(target_datetime.day).zfill(2)
    target_time = str(target_datetime.hour).zfill(2)
    return target_date, target_time

async def main(station_name: str) -> None:
    url_station = get_url(endpoint_name="station", station_name=station_name)
    station_xml = await fetch_xml(path=url_station)

    station_eva_code = parse_station_eva_code(station_xml)
    target_date, target_hour = get_target_time()
    url_plan = get_url(
        endpoint_name="plan",
        eva_number=station_eva_code,
        date=target_date,
        hour=target_hour,
    )
    url_fchg = get_url(
        endpoint_name="fchg",
        eva_number=station_eva_code,
    )

    plan_xml, fchg_xml = await asyncio.gather(
        fetch_xml(path=url_plan),
        fetch_xml(path=url_fchg),
    )
    fchg_updates = parse_fchg_updates(fchg_xml)
    station_snapshot = build_station_snapshot(
        plan_xml=plan_xml,
        station_name=station_name,
        station_eva_code=station_eva_code,
        fchg_updates=fchg_updates,
    )
    output_path = write_station_snapshot(station_snapshot)
    print(json.dumps(station_snapshot, indent=2, ensure_ascii=False))
    print(f"\nWrote snapshot to {output_path}")
        
if __name__ == "__main__":
    asyncio.run(main("Berlin Ostbahnhof"))
