# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.dependencies.mongo_db_authentication import connect_to_mongo, close_mongo_connection
from app.core.scheduler import start_scheduler
from app.routers import (
    handle_cron_tasks,
    handle_dashboard,
    handle_platform_insights, 
    handle_campaign_analysis,
    handle_settings, 
    handle_utils,
    handle_products_keywords,
    handle_settings,
)

app = FastAPI(title="Social Media API", description="API for Social Media Analysis", version="1.0.0")

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
app.include_router(handle_cron_tasks.router, prefix="/social-media/handle-cron-tasks", tags=["cron-tasks"])
app.include_router(handle_platform_insights.router, prefix="/social-media/platform-insights", tags=["platform-insights"])
app.include_router(handle_campaign_analysis.router, prefix="/social-media/campaign-analysis", tags=["campaign-analysis"])
app.include_router(handle_products_keywords.router, prefix="/social-media/products-keywords", tags=["products-keywords"])
app.include_router(handle_settings.router, prefix="/social-media/settings", tags=["settings"])
app.include_router(handle_utils.router, prefix="/social-media/utils", tags=["utils"])
app.include_router(handle_dashboard.router,prefix="/social-media/dashboard",tags=["dashboard"])

# Events
app.add_event_handler("startup", start_scheduler)
app.add_event_handler("startup", connect_to_mongo)

app.add_event_handler("shutdown", close_mongo_connection)



if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)