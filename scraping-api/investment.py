import yfinance as yf
import pandas
from tqdm import tqdm
import os
import json

info_db = pandas.read_csv('result/res1.csv')

company_details = {}

for company in tqdm(os.listdir('json')):
    trading_symbol = info_db.loc[info_db['name'] == company, 'symbol']
    if len(trading_symbol) == 0: continue
    trading_symbol = list(trading_symbol)[0]
    data = yf.Ticker(trading_symbol)
    
    company_info = data.info
    company_details[company] = {}

    company_details[company]['summary'] = company_info['longBusinessSummary']
    company_details[company]['market_cap'] = company_info['marketCap']
    company_details[company]['dividend_yield'] = company_info['dividendYield']


with open('company_details.json', 'w') as file:
    json.dump(company_details, file)