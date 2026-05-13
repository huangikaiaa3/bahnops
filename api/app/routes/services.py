from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection

from api.app.core.exceptions import ServiceNotFoundError
from api.app.db.session import get_db_connection
from api.app.schemas.service_changes import ServiceChangeResponse
from api.app.schemas.services import ServiceDetailResponse
from api.app.services.services import get_service_changes_response, get_service_detail_response

router = APIRouter(prefix="/services", tags=["services"])


@router.get("/{service_id}", response_model=ServiceDetailResponse)
async def get_service_data(service_id: int, connection: AsyncConnection = Depends(get_db_connection)) -> ServiceDetailResponse:
    try:
        service_detail = await get_service_detail_response(service_id=service_id, connection=connection)
        return service_detail
    except ServiceNotFoundError:
        raise HTTPException(status_code=404, detail="Service not found")


@router.get("/{service_id}/changes", response_model=list[ServiceChangeResponse])
async def get_service_changes(service_id: int, connection: AsyncConnection = Depends(get_db_connection)) -> list[ServiceChangeResponse]:
    try:
        changes = await get_service_changes_response(service_id=service_id, connection=connection)
        return changes
    except ServiceNotFoundError:
        raise HTTPException(status_code=404, detail="Service not found")
