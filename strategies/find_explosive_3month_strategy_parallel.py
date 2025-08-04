import pandas as pd
import numpy as np
import itertools
from datetime import timedelta
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import os
import time
from pathlib import Path

from macd_rsi_strategy import run_macd_rsi_strategy

# === 基本设置 ===
initial_cash = 10000
window_size = 63  # 精确63个交易日
data_path = '/mnt/data/data/tqqq.csv'
save_interval = 100
save_time_interval = 300

# === 输出目录 ===
output_path = Path('/mnt/data/backtest_results')
output_path.mkdir(parents=True, exist_ok=True)

# === 加载数据 ===
df = pd.read_csv(data_path)
df.columns = df.columns.str.strip().str.title()
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)
df.sort_index(inplace=True)

# === 参数组合 ===
macd_fast_list = [3, 4, 5]
macd_slow_list = [6, 8, 10]
macd_signal_list = [2, 4, 6]
rsi_window_list = [7, 14]
rsi_buy_list = [65, 70]
rsi_sell_list = [30, 35]

param_grid = list(itertools.product(
    macd_fast_list, macd_slow_list, macd_signal_list,
    rsi_window_list, rsi_buy_list, rsi_sell_list
))

# === 构造滑动窗口任务 ===
dates = df.index
start_dates = dates[:len(dates) - window_size]
task_list = list(itertools.product(start_dates, param_grid))

# === 回测函数 ===
def process_one_task(task):
    start_date, (macd_fast, macd_slow, macd_signal, rsi_window, rsi_buy, rsi_sell) = task

    if macd_fast >= macd_slow:
        return None

    try:
        if start_date not in df.index:
            return None
        start_loc = df.index.get_loc(start_date)
        end_loc = start_loc + window_size
        if end_loc > len(df):
            return None
        df_window = df.iloc[start_loc:end_loc].copy()

        result = run_macd_rsi_strategy(
            df_window,
            initial_cash=initial_cash,
            macd_fast=macd_fast,
            macd_slow=macd_slow,
            macd_signal=macd_signal,
            rsi_window=rsi_window,
            rsi_buy=rsi_buy,
            rsi_sell=rsi_sell,
            save_plots=False  # ✅ 不绘图，提升效率
        )

        return {
            'Start_Date': start_date.date(),
            'End_Date': df_window.index[-1].date(),
            'MACD_Fast': macd_fast,
            'MACD_Slow': macd_slow,
            'MACD_Signal': macd_signal,
            'RSI_Window': rsi_window,
            'RSI_Buy': rsi_buy,
            'RSI_Sell': rsi_sell,
            'Final_Value': result['final_value'],
            'Annual_Return': result['annual_return'],
            'Sharpe': result['sharpe_ratio'],
            'Max_Drawdown': result['max_drawdown']
        }

    except Exception as e:
        with open(output_path / 'error_log.txt', "a") as f:
            f.write(f"[ERROR] {start_date.date()} MACD({macd_fast},{macd_slow},{macd_signal}) "
                    f"RSI({rsi_window},{rsi_buy},{rsi_sell}): {str(e)}\n")
        return None

# === 并行运行 ===
all_results = []
last_save_time = time.time()
cpu_cores = max(cpu_count() - 1, 2)
success_count = 0
start_time = time.time()

with Pool(cpu_cores) as pool:
    with tqdm(total=len(task_list)) as pbar:
        for i, res in enumerate(pool.imap_unordered(process_one_task, task_list, chunksize=cpu_cores)):
            pbar.update()
            if res:
                all_results.append(res)
                success_count += 1

            # ⏱ 显示预计剩余时间
            elapsed = time.time() - start_time
            completed = i + 1
            if completed > 0:
                rate = elapsed / completed
                remaining = rate * (len(task_list) - completed)
                mins = int(remaining // 60)
                secs = int(remaining % 60)
                pbar.set_postfix_str(f"ETA: {mins}m {secs}s")

            # 定时保存
            if i % save_interval == 0 or (time.time() - last_save_time) > save_time_interval:
                df_all = pd.DataFrame(all_results)
                df_all.to_csv(output_path / 'all_3month_strategies.csv', index=False)

                if not df_all.empty:
                    best_row = df_all.loc[df_all['Final_Value'].idxmax()]
                    pd.DataFrame([best_row]).to_csv(output_path / 'explosive_strategy_result.csv', index=False)

                    over_16x = df_all[df_all['Final_Value'] >= initial_cash * 16]
                    over_16x.to_csv(output_path / 'explosive_over_16x.csv', index=False)

                print(f"✅ Saved {len(all_results)} results so far.")
                last_save_time = time.time()

# === 最终保存 ===
df_all = pd.DataFrame(all_results)
df_all.to_csv(output_path / 'all_3month_strategies.csv', index=False)

if not df_all.empty:
    best_row = df_all.loc[df_all['Final_Value'].idxmax()]
    pd.DataFrame([best_row]).to_csv(output_path / 'explosive_strategy_result.csv', index=False)

    over_16x = df_all[df_all['Final_Value'] >= initial_cash * 16]
    over_16x.to_csv(output_path / 'explosive_over_16x.csv', index=False)

print(f"🎯 回测完成，总共成功回测数量：{success_count}")

import subprocess
subprocess.run(['python3', '/mnt/data/upload_all_to_s3.py'])
