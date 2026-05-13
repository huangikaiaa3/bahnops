from datetime import datetime

from pydantic import BaseModel


class ServiceDetailResponse(BaseModel):
    service_id: int
    service_run_uid: str
    display_name: str | None
    category: str | None
    number: str | None
    line: str | None
    planned_arrival: datetime | None
    current_arrival: datetime | None
    planned_departure: datetime | None
    current_departure: datetime | None
    planned_arrival_platform: str | None
    current_arrival_platform: str | None
    planned_departure_platform: str | None
    current_departure_platform: str | None
    is_cancelled: bool
    last_seen_at: datetime
