import pandas as pd
import numpy as np

# 读取数据
df = pd.read_csv('btc_usd_daily_2016_2025.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# 计算SMA
df['SMA20'] = df['Close'].rolling(window=20).mean()
df['SMA50'] = df['Close'].rolling(window=50).mean()

# 计算RSI
def calculate_rsi(data, periods=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df['RSI'] = calculate_rsi(df['Close'])

# 买入信号：价格跌破SMA50后反弹，且RSI < 30
df['Buy_Signal'] = (df['Close'] < df['SMA50']) & (df['Close'].shift(1) > df['Close']) & (df['RSI'] < 30)

# 卖出信号：价格突破SMA20后回落，且RSI > 70
df['Sell_Signal'] = (df['Close'] > df['SMA20']) & (df['Close'].shift(1) < df['Close']) & (df['RSI'] > 70)

# 提取买卖点
buy_points = df[df['Buy_Signal']][['Timestamp', 'Close', 'RSI', 'SMA50']]
sell_points = df[df['Sell_Signal']][['Timestamp', 'Close', 'RSI', 'SMA20']]

print("买入点：")
print(buy_points)
print("\n卖出点：")
print(sell_points)

# 保存结果
df.to_csv('btc_analysis_with_signals.csv', index=False)