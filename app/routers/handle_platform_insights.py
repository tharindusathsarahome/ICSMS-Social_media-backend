# app/routers/handle_platform_insights.py

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.dependencies.mongo_db_authentication import get_database
from app.dependencies.user_authentication import role_required
from app.db.platform_insights_data import get_platform_insights_data
import json

router = APIRouter()


@router.get("/platform_insights_data")
async def platform_insights_data(
    db: MongoClient = Depends(get_database),
    # current_user=Depends(role_required("User")),
    startDate: str = Query(..., title="Start Date"),
    endDate: str = Query(..., title="End Date")
):
    # try:
        result = get_platform_insights_data(db, startDate, endDate)
        serialized_posts = jsonable_encoder(result)
        return JSONResponse(content=serialized_posts)
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Error[Platform Insights]: {str(e)}")
