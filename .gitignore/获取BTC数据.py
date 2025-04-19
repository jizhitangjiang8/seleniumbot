import yfinance as yf
import pandas as pd
from datetime import datetime

def fetch_yahoo_data():
    btc_usd = yf.download('BTC-USD', start='2016-01-01', end=datetime.today().strftime('%Y-%m-%d'), interval='1d', auto_adjust=False)
    btc_usd.reset_index(inplace=True)
    btc_usd = btc_usd[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    btc_usd.columns = ['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume']
    btc_usd.to_csv('btc_usd_daily_2016_2025.csv', index=False)
    print("日级别数据已保存到 btc_usd_daily_2016_2025.csv")

fetch_yahoo_data()