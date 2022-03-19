import yfinance as yf
import pandas
from tqdm import tqdm
import os
import json

info_db = pandas.read_csv('result/res1.csv')

high_low = {}

for company in tqdm(os.listdir('json')):
    trading_symbol = info_db.loc[info_db['name'] == company, 'symbol']
    if len(trading_symbol) == 0: continue
    trading_symbol = list(trading_symbol)[0]
    data = yf.download(trading_symbol, '2021-03-20', '2022-03-19')

    high_low[company] = {}
    high_low[company]['high'] = max(data['High'])
    high_low[company]['low'] = max(data['Low'])

with open('high_low.json', 'w') as file:
    json.dump(high_low, file)