import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo

def parse_station_info(station_xml: str) -> tuple[str, str]:
    root = ET.fromstring(station_xml)
    station = root.find("station")
    if station is None:
        raise ValueError("No station element found in station response")

    station_name = station.attrib["name"]
    station_eva_code = station.attrib["eva"]
    
    return station_name, station_eva_code

def _parse_station_plan(plan_xml: str) -> list[dict]:
    root = ET.fromstring(plan_xml)
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

        services.append(
            {
                "service_id": service.attrib.get("id"),
                "category": tl.attrib.get("c") if tl is not None else None,
                "number": tl.attrib.get("n") if tl is not None else None,
                "line": line,
                "display_name": display_name,
                "planned_arrival": ar.attrib.get("pt") if ar is not None else None,
                "planned_departure": dp.attrib.get("pt") if dp is not None else None,
                "planned_arrival_platform": ar.attrib.get("pp") if ar is not None else None,
                "planned_departure_platform": dp.attrib.get("pp") if dp is not None else None,
                "planned_arrival_path": planned_arrival_path,
                "planned_departure_path": planned_departure_path,
            }
        )

    return services

def _parse_fchg_updates(fchg_xml: str) -> dict[str, dict]:
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

def normalize_station_snapshot(station_xml: str, plan_xml: str, fchg_xml: str | None = None,) -> dict:
    station_name, station_eva_number = parse_station_info(station_xml)
    planned_services = _parse_station_plan(plan_xml)
    fchg_updates = _parse_fchg_updates(fchg_xml) if fchg_xml is not None else {}

    services = []

    for planned_service in planned_services:
        service_id = planned_service["service_id"]
        current_update = fchg_updates.get(service_id, {})

        services.append({
            "service_id": service_id,
            "category": planned_service["category"],
            "number": planned_service["number"],
            "line": planned_service["line"],
            "display_name": planned_service["display_name"],
            "planned_arrival": planned_service["planned_arrival"],
            "planned_departure": planned_service["planned_departure"],
            "current_arrival": current_update.get("current_arrival"),
            "current_departure": current_update.get("current_departure"),
            "planned_arrival_platform": planned_service["planned_arrival_platform"],
            "planned_departure_platform": planned_service["planned_departure_platform"],
            "current_arrival_platform": current_update.get("current_arrival_platform"),
            "current_departure_platform": current_update.get("current_departure_platform"),
            "planned_arrival_path": planned_service["planned_arrival_path"],
            "planned_departure_path": planned_service["planned_departure_path"],
            "current_arrival_path": current_update.get("current_arrival_path", []),
            "current_departure_path": current_update.get("current_departure_path", []),
        })

    return {
        "captured_at": datetime.now(ZoneInfo("Europe/Berlin")).isoformat(),
        "station": {
            "name": station_name,
            "eva_number": station_eva_number,
        },
        "services": services,
    }
