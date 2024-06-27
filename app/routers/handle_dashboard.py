
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from fastapi.encoders import jsonable_encoder



from app.db.dashboard_data import get_facebook_analysis_data
from app.db.dashboard_data import get_products_trend_data,get_keyword_trend_data,get_setiment_percentage
from app.dependencies.mongo_db_authentication import get_database

router = APIRouter()

@router.get('/facebook_analysis_data')
async def facebook_analysis_data(
    db: MongoClient = Depends(get_database),
    startDate: str = Query(..., title="Start Date"),
    endDate: str = Query(..., title="End Date")
):
    try:
        result = get_facebook_analysis_data(db, startDate, endDate)
        serialized_posts = jsonable_encoder(result)
        return JSONResponse(content=serialized_posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    

@router.get('/product_trend_data')
async def product_trend_data(
    db: MongoClient = Depends(get_database),
    startDate: str = Query(..., title="Start Date"),
    endDate: str = Query(..., title="End Date")
):
    try:
        result = get_products_trend_data(db, startDate, endDate)
        serialized_posts = jsonable_encoder(result)
        return JSONResponse(content=serialized_posts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    
    
@router.get('/keyword_trend_data')
async def keyword_trend_data(
    db:MongoClient = Depends(get_database),
    startDate: str = Query(..., title="Start Date"),
    endDate: str = Query(..., title="End Date")
):
    try:
        result = get_keyword_trend_data(db,startDate,endDate)
        serialized_posts = jsonable_encoder(result)
        return JSONResponse(content=serialized_posts)
    
    except Exception as e:
        raise HTTPException(status_code=500,detail=f"error:{str(e)}")
    
    
@router.get("/get_setiment_percentage", response_model=dict)
async def analyze_sentiment(
    db: MongoClient = Depends(get_database)
):
    try:
        sentiment_analysis_data =  get_setiment_percentage(db)
        return sentiment_analysis_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




