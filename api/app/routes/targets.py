from fastapi import APIRouter, Depends
from psycopg import Connection

from api.app.db.session import get_db_connection
from api.app.repositories.targets import get_targets
from api.app.schemas.targets import TargetResponse


router = APIRouter(prefix="/targets", tags=["targets"])


@router.get("", response_model=list[TargetResponse])
async def list_targets(connection: Connection = Depends(get_db_connection)) -> list[TargetResponse]:
    targets = get_targets(connection=connection)
    return targets
