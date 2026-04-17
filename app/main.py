from fastapi import FastAPI
from app.core.config import get_settings
from app.routers.routers import router as credits_router
import app.models

settings = get_settings()

app = FastAPI()

app.include_router(credits_router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": settings.APP_NAME, "env": settings.APP_ENV}
