from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection

from api.app.db.session import get_db_connection
from api.app.repositories.stations import (
    get_station_by_eva_number,
    get_station_services_by_eva_number,
)
from api.app.schemas.station_services import StationServiceResponse


router = APIRouter(prefix="/stations", tags=["stations"])


@router.get("/{eva_number}/services", response_model=list[StationServiceResponse])
async def get_station_services(eva_number: str, connection: Connection = Depends(get_db_connection),) -> list[StationServiceResponse]:
    station = get_station_by_eva_number(eva_number=eva_number, connection=connection)

    if station is None:
        raise HTTPException(status_code=404, detail="Station not found")

    services = get_station_services_by_eva_number(eva_number=eva_number, connection=connection)
    return services
