# -*- coding: utf-8 -*-

import pandas as pd
import pandas_datareader as web
import yfinance as yf
import datetime as dt
import matplotlib.pyplot as plt
import mplfinance as mpl
import numpy as np
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots
# import plotly.graph_objects as go
import requests
import os 
from api_key import line_notify_api, line_notify_token


def send_line_notify(notification_message):
    """
    LINEに通知する
    """
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    data = {'message': f'message: {notification_message}'}
    requests.post(line_notify_api, headers = headers, data = data)
   

# df = pd.read_csv('/home/yamadakoki/yamada/stock_trade/symbols/japan_symbols.csv', encoding='SHIFT-JIS')
print(os.path.isdir('/home/yamadakoki/yamada/stock_trade/symbols/'))
df = pd.read_csv('/home/yamadakoki/yamada/stock_trade/symbols/sandp500.csv')
symbols = []
content = '\n\nToday`s stock report' + str(dt.date.today())
small_symbols = ''
small_cap = 0
no_signal = 0
count = 0

print(df.head())

#----------------------------------------------------------------------------
# for symbol in df['symbol'][1000:1100] :  
#     x = str(symbol) + '.T'
# #     print(x)
#     symbols.append(x)
for symbol in df['symbol']:
    symbols.append(symbol)

for symbol in symbols:
    # 150日間で調べる
    start=dt.datetime.now()-dt.timedelta(days=150)
    end=dt.datetime.now()
    count += 1
    print(count)
   
    try:
        symbol_df = yf.download(symbol, start, end, interval='1d')
        market_capdata = web.get_quote_yahoo(symbol)['marketCap']
        market_cap = int(str(market_capdata).split()[1])
        print('時価総額は'+ str(market_cap))
       
    except:
        print('時価総額なし'+str(symbol))
       
    if symbol_df.empty:
        continue
       
    print(symbol)
   
   
   
    
    # 標準偏差を計算
    try:
        # high in the past 81 days
        symbol_df['Highest81'] = symbol_df['Adj Close'].rolling(window=81).max()
        short_sma = 25
        symbol_df['SMA'+str(short_sma)] = symbol_df['Adj Close'].rolling(window=short_sma).mean()
        symbol_df['STD'] = symbol_df['Adj Close'].rolling(window=25).std()
        symbol_df['Standard_deviation_normalization'] = 100 * 2 * symbol_df['STD'] / symbol_df['SMA'+str(short_sma)]

        # print(symbol_df['Highest81'])
        # print(symbol_df.tail())

        highest = symbol_df['Highest81'][-2]
        close = symbol_df['Adj Close'][-1]
        std = symbol_df['Standard_deviation_normalization'][-1]
       
    except Exception as e:
        print(e)
        continue
   
    if std < 3 and close > 0.96 * highest:
        print('signal')
        if market_cap < 30000000000:
            print('market_cap is too small')
            small_symbols += symbol + '\n'
            small_cap += 1
            continue
        content_x = "\n{} 👍 \n逆指値を入れる値段: ¥{}\n前の終値: ¥{}".format(symbol, round(highest, 5), round(close, 5))
        content += '\n'+content_x  
    else :
        print('No signal')
        no_signal += 1
       
print(content)
print('Is signal but Too Small Symbols is {}'.format(small_cap))
print(small_symbols)
print('No signal Symbols is {}'.format(no_signal))
# send_line_notify(content)
