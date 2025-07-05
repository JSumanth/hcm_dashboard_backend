from fastapi import FastAPI
from dashboard_routes import router as dashboard_router
from mangum import Mangum
app = FastAPI()
app.include_router(dashboard_router)
handler = Mangum(app)