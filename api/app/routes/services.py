from fastapi import APIRouter, Depends, HTTPException
from psycopg import AsyncConnection

from api.app.db.session import get_db_connection
from api.app.repositories.services import get_service_by_id, get_service_changes_by_id
from api.app.schemas.service_changes import ServiceChangeResponse
from api.app.schemas.services import ServiceDetailResponse

router = APIRouter(prefix="/services", tags=["services"])


@router.get("/{service_id}", response_model=ServiceDetailResponse)
async def get_service_data(service_id: int, connection: AsyncConnection = Depends(get_db_connection)) -> ServiceDetailResponse:
    service_detail = await get_service_by_id(service_id=service_id, connection=connection)

    if service_detail is None:
        raise HTTPException(status_code=404, detail="Service not found")

    return service_detail


@router.get("/{service_id}/changes", response_model=list[ServiceChangeResponse])
async def get_service_changes(service_id: int, connection: AsyncConnection = Depends(get_db_connection)) -> list[ServiceChangeResponse]:
    service = await get_service_by_id(service_id=service_id, connection=connection)

    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    changes = await get_service_changes_by_id(service_id=service_id, connection=connection)
    return changes
