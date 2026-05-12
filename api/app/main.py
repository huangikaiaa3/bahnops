from fastapi import FastAPI
from api.app.routes.health import router as health_router
from api.app.routes.services import router as services_router
from api.app.routes.stations import router as stations_router
from api.app.routes.targets import router as targets_router

app = FastAPI(title="BahnOps")

app.include_router(health_router)
app.include_router(services_router)
app.include_router(stations_router)
app.include_router(targets_router)
