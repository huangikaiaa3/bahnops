from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection

from api.app.core.exceptions import StationNotFoundError
from api.app.db.session import get_db_connection
from api.app.schemas.station_services import StationServiceResponse
from api.app.services.stations import get_station_services_response


router = APIRouter(prefix="/stations", tags=["stations"])


@router.get("/{eva_number}/services", response_model=list[StationServiceResponse])
async def get_station_services(eva_number: str, connection: AsyncConnection = Depends(get_db_connection)) -> list[StationServiceResponse]:
    try:
        services = await get_station_services_response(eva_number=eva_number, connection=connection)
        return services
    except StationNotFoundError:
        raise HTTPException(status_code=404, detail="Station not found")
