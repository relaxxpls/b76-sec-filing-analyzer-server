import json
import config
from fastapi import FastAPI
from pymongo import MongoClient
from fastapi import Body, FastAPI, status
from fastapi.responses import JSONResponse

client = MongoClient()

db = client[config.DBNAME]

app = FastAPI()

@app.get('/api/company/{cik}')
async def getCompanyData(cik):
    try:
        return JSONResponse(content=db['company_data'].find_one({'cik' : cik})['data'])
    except:
        return JSONResponse(content={},status_code=status.HTTP_404_NOT_FOUND)