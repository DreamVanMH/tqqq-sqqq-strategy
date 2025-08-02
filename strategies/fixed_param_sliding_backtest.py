import pandas as pd
import sqlite3
from tqdm import tqdm
from macd_rsi_strategy import run_macd_rsi_strategy

# === 参数设置 ===
data_path = '/mnt/data/data/tqqq.csv'
output_path = '/mnt/data/backtest_results/fixed_param_window_backtest.csv'
window_size = 63
initial_cash = 10000

# 固定参数
params = {
    'macd_fast': 5,
    'macd_slow': 10,
    'macd_signal': 4,
    'rsi_window': 14,
    'rsi_buy': 65,
    'rsi_sell': 30
}

# === 读取数据 ===
df = pd.read_csv(data_path)
df.columns = df.columns.str.strip().str.title()
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)
df.sort_index(inplace=True)

# === 滑动窗口回测（每天滚动 + 进度条）===
results = []
dates = df.index
total_steps = len(dates) - window_size

with tqdm(total=total_steps, desc="📈 回测进度") as pbar:
    for i in range(total_steps):
        start_date = dates[i]
        end_date = dates[i + window_size - 1]
        window_df = df.loc[start_date:end_date].copy()

        try:
            result = run_macd_rsi_strategy(
                df=window_df,
                initial_cash=initial_cash,
                **params
            )

            results.append({
                'Start_Date': start_date.date(),
                'End_Date': end_date.date(),
                'Final_Value': result['final_value'],
                'Annual_Return': result['annual_return'],
                'Sharpe': result['sharpe_ratio'],
                'Max_Drawdown': result['max_drawdown'],
                #'BuyHold_Value': window_df['BuyHold'].iloc[-1]
            })

        except Exception as e:
            print(f"⚠️ 跳过区间 {start_date.date()} ~ {end_date.date()}，错误：{e}")

        pbar.update(1)

# === 保存结果 ===
results_df = pd.DataFrame(results)
results_df.to_csv(output_path, index=False)
print(f"\n✅ 完成：共回测 {len(results_df)} 个窗口，结果保存至：{output_path}")
