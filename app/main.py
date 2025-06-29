from fastapi import FastAPI
from app.dashboard_routes import router as dashboard_router

app = FastAPI()
app.include_router(dashboard_router)
