from unicodedata import name
import pandas as pd
import requests
import json
import sys

  
sys.path.insert(0, '../')

from models import Company
from database import SessionLocal

BASE_URL_CIK = 'https://data.sec.gov/submissions/'

cik_df = pd.read_csv('../data/res.csv', usecols=['name','cik'])

try:
    db = SessionLocal()
except:
    exit()


for index,record in cik_df.iterrows():
    
    if pd.isna(record['cik']):
        print("CIK not available")
        continue
    cik = str(int(record['cik']))
    cik = '0'*(10-len(cik)) + cik
    url = BASE_URL_CIK + 'CIK' + cik + '.json'
    res = requests.get(url, headers={'user-agent':"interIIT krishna@inter.com",'Accept-Encoding':'gzip, deflate, br'})
    try:
        data = json.loads(res.text)
    except:
        print("error",record['name'])
        continue
    new_company = Company()
    new_company.cik = cik
    if not data.get('name'):
        print("error",record['name'])
        continue
    new_company.name = data.get('name')
    new_company.sic = data.get('sicDescription')
    new_company.state_incorp = data.get('stateOfIncorporation')
    tickers = data.get('tickers')
    tickr = ""
    for tick in tickers:
        tickr = tickr + tick +  ", "
    tickr = tickr[:-2] 
    new_company.ticker = tickr
    addrs = data.get('addresses')
    addr = addrs.get('mailing')
    street = addr.get('street1') if addr.get('street1')!=None else " "
    city = addr.get('city') if addr.get('city')!=None else " "
    state = addr.get('stateOrCountry') if addr.get('stateOrCountry')!=None else " "
    zipCode = addr.get('zipCode') if addr.get('zipCode')!=None else " "
    address = street +", "+ city+", "+ state + ", "+ zipCode
    new_company.mailing_addr = address
    new_company.category = data.get("category") if addr.get('category')!=None else " "
    try:
        db.add(new_company)
        db.commit()    
    except Exception as e:
        print(e)
        print(cik, data.get('name'))


db.close()