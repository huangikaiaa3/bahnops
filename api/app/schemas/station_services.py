from datetime import datetime

from pydantic import BaseModel


class StationServiceResponse(BaseModel):
    service_id: int
    display_name: str | None
    category: str | None
    number: str | None
    line: str | None
    planned_arrival: str | None
    current_arrival: str | None
    planned_departure: str | None
    current_departure: str | None
    planned_arrival_platform: str | None
    current_arrival_platform: str | None
    planned_departure_platform: str | None
    current_departure_platform: str | None
    is_cancelled: bool
    last_seen_at: datetime