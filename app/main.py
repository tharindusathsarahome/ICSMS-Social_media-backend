# app/main.py

from fastapi import FastAPI
from app.routers import handle_posts
from app.db.connection import connect_to_mongo, close_mongo_connection

app = FastAPI()

# Routers
app.include_router(handle_posts.router, prefix="/social-media", tags=["social_media"])

# Events
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)
