import pandas as pd
import numpy as np
import itertools
from datetime import timedelta
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import os
import time
from pathlib import Path
import subprocess

from macd_rsi_strategy import run_macd_rsi_strategy

# === 基本设置 ===
initial_cash = 10000
window_size = 63
data_path = '/mnt/data/data/sqqq.csv'
save_interval = 100
save_time_interval = 300

output_path = Path('/mnt/data/backtest_results_sqqq')
output_path.mkdir(parents=True, exist_ok=True)
existing_file = output_path / 'all_3month_strategies_sqqq.csv'

# === 加载数据 ===
df = pd.read_csv(data_path)
df.columns = df.columns.str.strip().str.title()
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)
df.sort_index(inplace=True)

# === 枚举参数组合 ===
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

dates = df.index
start_dates = dates[:len(dates) - window_size]
task_list_all = list(itertools.product(start_dates, param_grid))

# === 加载已完成任务（断点续跑） ===
done_tasks = {}
if existing_file.exists():
    try:
        df_existing = pd.read_csv(existing_file)
        df_existing['Start_Date'] = pd.to_datetime(df_existing['Start_Date'])
        for _, row in df_existing.iterrows():
            key = (
                row['Start_Date'].date(),
                row['MACD_Fast'], row['MACD_Slow'], row['MACD_Signal'],
                row['RSI_Window'], row['RSI_Buy'], row['RSI_Sell']
            )
            done_tasks[key] = row.to_dict()
        print(f"✅ 已加载已完成任务数量: {len(done_tasks)}")
    except Exception as e:
        print(f"⚠️ 无法读取历史结果: {e}")

# === 过滤未完成任务 ===
def is_task_done(task):
    start_date, (macd_fast, macd_slow, macd_signal, rsi_window, rsi_buy, rsi_sell) = task
    return (
        start_date.date(),
        macd_fast, macd_slow, macd_signal,
        rsi_window, rsi_buy, rsi_sell
    ) in done_tasks

task_list = [task for task in task_list_all if not is_task_done(task)]
print(f"🧮 待执行任务数量: {len(task_list)} / 总任务数: {len(task_list_all)}")

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
            save_plots=False,
            verbose=False
        )

        return {
            'Start_Date': start_date.strftime('%Y-%m-%d'),
            'End_Date': df_window.index[-1].strftime('%Y-%m-%d'),
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

# === 并行执行任务 ===
new_results = {}
last_save_time = time.time()
cpu_cores = max(cpu_count() - 1, 2)
success_count = 0
start_time = time.time()

print(f"🧪 Starting backtest with {len(task_list):,} tasks using {cpu_cores} CPU cores...")

with Pool(cpu_cores) as pool:
    with tqdm(total=len(task_list)) as pbar:
        for i, res in enumerate(pool.imap_unordered(process_one_task, task_list, chunksize=cpu_cores)):
            pbar.update()

            if res:
                key = (
                    pd.to_datetime(res['Start_Date']).date(),
                    res['MACD_Fast'], res['MACD_Slow'], res['MACD_Signal'],
                    res['RSI_Window'], res['RSI_Buy'], res['RSI_Sell']
                )
                new_results[key] = res
                success_count += 1

            # ETA 显示
            elapsed = time.time() - start_time
            completed = i + 1
            if completed > 0:
                rate = elapsed / completed
                remaining = rate * (len(task_list) - completed)
                mins = int(remaining // 60)
                secs = int(remaining % 60)
                pbar.set_postfix_str(f"ETA: {mins}m {secs}s")

            # 定期保存
            if i % save_interval == 0 or (time.time() - last_save_time) > save_time_interval:
                all_results = list(done_tasks.values()) + list(new_results.values())
                df_all = pd.DataFrame(all_results)
                df_all.to_csv(existing_file, index=False)

                if not df_all.empty:
                    best_row = df_all.loc[df_all['Final_Value'].idxmax()]
                    pd.DataFrame([best_row]).to_csv(output_path / 'explosive_strategy_result_sqqq.csv', index=False)
                    over_16x = df_all[df_all['Final_Value'] >= initial_cash * 16]
                    over_16x.to_csv(output_path / 'explosive_over_16x_sqqq.csv', index=False)

                print(f"✅ Saved {len(df_all)} results so far.")
                last_save_time = time.time()

# === 最终保存 ===
all_results = list(done_tasks.values()) + list(new_results.values())
df_all = pd.DataFrame(all_results)
df_all.to_csv(existing_file, index=False)

if not df_all.empty:
    best_row = df_all.loc[df_all['Final_Value'].idxmax()]
    pd.DataFrame([best_row]).to_csv(output_path / 'explosive_strategy_result_sqqq.csv', index=False)
    over_16x = df_all[df_all['Final_Value'] >= initial_cash * 16]
    over_16x.to_csv(output_path / 'explosive_over_16x_sqqq.csv', index=False)

print(f"\n🎯 SQQQ回测完成，总共成功回测数量：{success_count}")

# 可选上传
subprocess.run(['python3', '/mnt/data/upload_all_to_s3.py'])
