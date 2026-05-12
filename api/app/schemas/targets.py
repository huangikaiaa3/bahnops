from pydantic import BaseModel


class TargetResponse(BaseModel):
    id: int
    station_id: int
    station_eva_number: str
    station_name: str
    target_type: str
    poll_interval_seconds: int
    is_active: bool
