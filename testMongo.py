from fastapi import FastAPI, Query, APIRouter
from pymongo import MongoClient
import json

app = FastAPI()
router = APIRouter()

client = MongoClient("mongodb://localhost:27017/")
db = client["icsms_backend"]

# uvicorn testMongo:app --reload

@router.get("/execute_mongodb_query")
async def execute_mongodb_query(query: str = Query(..., title="MongoDB Query")):
    try:
        query_dict = json.loads(query)
        result = db.command(query_dict)
        return result
    except Exception as e:
        return {"error": str(e)}

app.include_router(router)

# http://127.0.0.1:8000/execute_mongodb_query?query={"insert":"SocialMedia","documents":[{"sm_id":"SM01","name":"Facebook"},{"sm_id":"SM02","name":"Instagram"}]}
