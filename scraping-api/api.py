from datetime import datetime
import os
from sec_api import XbrlApi
import pandas 
import requests
import json
import random
from tqdm import tqdm

BASE_URL_CIK = 'https://data.sec.gov/submissions/'
API_KEY = "bc91833a1bf76a681a9605b479eaXXXXXXXXXXXXXXd4a6e"

xbrlApi = XbrlApi(api_key=API_KEY)

companies_list = pandas.read_csv('data/saas_list.csv', usecols=['Company'])['Company'].to_list()

cik_df = pandas.read_csv('result/res.csv', usecols=['name','cik'])

for company in tqdm(companies_list):
    [record] = cik_df.index[cik_df['name'] == company]
    try: cik = str(int(cik_df.at[record,'cik']))
    except: 
        print('here')
        continue
    if pandas.isna(cik):
        print("CIK not available")
        continue
    cik = '0'*(10-len(cik)) + cik
    
    url = BASE_URL_CIK + 'CIK' + cik + '.json'
    res = requests.get(url, headers={'user-agent':"interIIT krishna@interIIT.com",'Accept-Encoding':'gzip, deflate, br'})
    data = json.loads(res.text)
    
    recent_filings = data["filings"]['recent']
    accession_no = recent_filings['accessionNumber']
    accepted_on =  recent_filings['acceptanceDateTime'] 
    form_type = recent_filings['form']
    
    scraped_indices = []
    
    for i in range(len(accepted_on)):
        sub_date = datetime.strptime(accepted_on[i],"%Y-%m-%dT%H:%M:%S.%fZ")
        if sub_date<datetime(2020,1,1,0,0):
            break
        if form_type[i]=='10-K' or form_type[i]=='10-Q':
            scraped_indices.append(i)
    
    for i in scraped_indices:
        xbrl_json = xbrlApi.xbrl_to_json(accession_no=accession_no[i])
        try:
            os.makedirs("json_/"+company)
        except:
            pass
        filename = "json_/"+company +'/'+ form_type[i]+"_"+accepted_on[i][0:10]+".json"
        while os.path.exists(filename):
            filename = "json_/"+company +'/'+ form_type[i]+"_"+accepted_on[i][0:10]+"_"+str(random.randrange(1,10))+".json"
 
        with open(os.path.join(filename),'x',encoding="utf-8") as m:
             json.dump(xbrl_json,m, indent=4)   
