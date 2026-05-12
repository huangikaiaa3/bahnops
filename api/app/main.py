from fastapi import FastAPI
from api.app.routes.health import router as health_router
from api.app.routes.boards import router as board_router
from api.app.routes.services import router as services_router
from api.app.routes.tracked_targets import router as tracked_targets_router

app = FastAPI(title="BahnOps")

app.include_router(health_router)
app.include_router(board_router)
app.include_router(services_router)
app.include_router(tracked_targets_router)