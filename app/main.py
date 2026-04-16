from fastapi import FastAPI
from app.routers.routers import router as credits_router
import app.models

app = FastAPI()

app.include_router(credits_router)