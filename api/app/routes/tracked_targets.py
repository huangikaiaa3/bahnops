from fastapi import APIRouter, Depends
from psycopg import Connection

from api.app.db.session import get_db_connection
from api.app.repositories.tracked_targets import get_tracked_targets
from api.app.schemas.tracked_targets import TrackedTargetResponse


router = APIRouter(prefix="/tracked-targets", tags=["tracked-targets"])


@router.get("", response_model=list[TrackedTargetResponse])
async def list_tracked_targets(connection: Connection = Depends(get_db_connection)) -> list[TrackedTargetResponse]:
    tracked_targets = get_tracked_targets(connection=connection)
    return tracked_targets
