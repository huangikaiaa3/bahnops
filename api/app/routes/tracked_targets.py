from fastapi import APIRouter, Depends
from api.app.schemas.tracked_targets import TrackedTargetResponse
from api.app.db import get_db_connection
from api.app.queries.tracked_targets import get_tracked_targets
from psycopg import Connection

router = APIRouter(prefix="/tracked-targets", tags=["tracked-targets"])

@router.get("", response_model=list[TrackedTargetResponse])
async def list_tracked_targets(connection: Connection = Depends(get_db_connection)) -> list[TrackedTargetResponse]:
    tracked_targets = get_tracked_targets(connection=connection)
    return tracked_targets