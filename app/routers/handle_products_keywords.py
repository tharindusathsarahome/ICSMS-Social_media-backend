# app/routers/handle_platform_insights.py

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pymongo.mongo_client import MongoClient
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.dependencies.mongo_db_authentication import get_database
from app.db.products_keywords_data import add_custom_products, get_custom_products, add_identified_products, get_identified_products
import json

router = APIRouter()


@router.get("/add_custom_product")
async def add_custom_products_route(
    db: MongoClient = Depends(get_database),
    custom_product: str = Query(..., title="Custom Product")
):
    try:
        result = add_custom_products(db, custom_product)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[Add Custom Products]: {str(e)}")
    

@router.get("/get_custom_products")
async def get_custom_products_route(
    db: MongoClient = Depends(get_database)
):
    try:
        result = get_custom_products(db)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[Get Custom Products]: {str(e)}")


@router.get("/add_identified_product")
async def add_identified_products_route(
    db: MongoClient = Depends(get_database)
):
    try:
        result = add_identified_products(db)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error[Add Identified Products]: {str(e)}")


@router.get("/get_identified_products")
async def get_identified_products_route(
    db: MongoClient = Depends(get_database)
):
    # try:
        result = get_identified_products(db)
        return JSONResponse(content=result)
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Error[Get Identified Products]: {str(e)}")