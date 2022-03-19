import json
import config
from fastapi import FastAPI
from pymongo import MongoClient

client = MongoClient()

db = client[config.DBNAME]

app = FastAPI()

@app.get('/api/company/{cik}')
async def getCompanyData(cik):
    return db['company_data'].find_one({'cik' : cik})