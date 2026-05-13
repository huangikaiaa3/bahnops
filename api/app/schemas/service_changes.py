from datetime import datetime

from pydantic import BaseModel


class ServiceChangeResponse(BaseModel):
    service_id: int
    poll_run_id: int
    event_time: datetime
    event_type: str
    old_value: str | None
    new_value: str | None
