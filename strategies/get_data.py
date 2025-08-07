# get_data.py

import yfinance as yf
import pandas as pd
import os

def get_price_data(symbol, start="2014-01-01", end=None, interval="1d", save_csv=False, csv_path=None):
    """
    拉取指定股票的历史价格数据，并重排为：Date, Close, High, Low, Open, Volume 格式

    参数:
    - symbol: 股票代码（如 "TQQQ"）
    - start: 开始时间（"YYYY-MM-DD"）
    - end: 结束时间（默认是今天）
    - interval: 数据间隔（如 "1d", "1h", "1m"）
    - save_csv: 是否保存为本地CSV
    - csv_path: 保存路径（如果为None则自动根据symbol命名）

    返回:
    - DataFrame，index 为日期，包含 Date, Close, High, Low, Open, Volume 列
    """
    df = yf.download(symbol, start=start, end=end, interval=interval, progress=False)

    if df.empty:
        raise ValueError(f"❌ 无法获取 {symbol} 的行情数据，请检查代码或网络")

    df = df[['Close', 'High', 'Low', 'Open', 'Volume']].copy()
    df.reset_index(inplace=True)  # 把日期列变成普通列
    df['Date'] = pd.to_datetime(df['Date'])  # 明确设置格式

    # 列顺序与原始csv一致
    df = df[['Date', 'Close', 'High', 'Low', 'Open', 'Volume']]
    df.sort_values('Date', inplace=True)

    if save_csv:
        if csv_path is None:
            csv_path = f"{symbol.lower()}_{interval}.csv"
        df.to_csv(csv_path, index=False)
        print(f"✅ 数据已保存到: {csv_path}")

    return df
