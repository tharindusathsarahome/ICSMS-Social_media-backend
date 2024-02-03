# app/main.py

from fastapi import FastAPI
from app.api.endpoints import social_media
from app.db.database import connect_to_mongo, close_mongo_connection

app = FastAPI()

# Routers
app.include_router(social_media.router, prefix="/social-media", tags=["social_media"])

# Events
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)
