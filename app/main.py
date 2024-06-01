# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.dependencies.mongo_db_authentication import connect_to_mongo, close_mongo_connection
from app.routers import (
    handle_facebook, 
    handle_platform_insights, 
    handle_settings, 
    utils,
)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Routers
app.include_router(handle_facebook.router, prefix="/handle-facebook", tags=["facebook"])
app.include_router(handle_platform_insights.router, prefix="/platform-insights", tags=["platform-insights"])
app.include_router(handle_settings.router, prefix="/settings", tags=["settings"])
app.include_router(utils.router, prefix="/utils", tags=["utils"])

# Events
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)
