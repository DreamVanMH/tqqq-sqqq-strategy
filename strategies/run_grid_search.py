# run_grid_search.py

import pandas as pd
import os
from datetime import datetime
from grid_search import grid_search_macd_rsi  # ✅ 修正后的导入

# 读取数据
df = pd.read_csv('/mnt/data/data/tqqq.csv', skiprows=2)
df.columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)
df = df.loc['2014-01-01':'2024-12-31'].copy()

# 网格搜索（初始资金 $10,000）
results_df = grid_search_macd_rsi(df, initial_cash=10000)

# 保存结果
output_dir = "/mnt/data/backtest_results"
os.makedirs(output_dir, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
results_df.to_csv(f"{output_dir}/tqqq_grid_search_results_{timestamp}.csv", index=False)

# 打印前5名策略组合
top_results = results_df.sort_values(by="Final_Value", ascending=False).head(5)

print("\n=== Top 5 Strategies ===")
print(top_results)
