import pandas as pd
import itertools
import time
from tqdm import tqdm
from datetime import datetime
from pathlib import Path
from macd_rsi_strategy import run_macd_rsi_strategy

# === 基本设置 ===
initial_cash = 10000
window_size = 63  # 约 3 个月交易日
data_path = '/mnt/data/data/tqqq.csv'
save_path = '/mnt/data/backtest_results/'
Path(save_path).mkdir(parents=True, exist_ok=True)

# === 读取数据 ===
df = pd.read_csv(data_path)
df.columns = df.columns.str.strip().str.title()
df['Date'] = pd.to_datetime(df['Date'])
df.set_index('Date', inplace=True)
df.sort_index(inplace=True)

# === 参数组合列表 ===
macd_fast_list = [3, 4, 5]
macd_slow_list = [6, 8, 10]
macd_signal_list = [2, 3, 4]
rsi_window_list = [4, 5, 6]
rsi_buy_list = [15, 20, 25]
rsi_sell_list = [75, 80, 85]

param_grid = list(itertools.product(
    macd_fast_list,
    macd_slow_list,
    macd_signal_list,
    rsi_window_list,
    rsi_buy_list,
    rsi_sell_list
))

# === 初始化记录 ===
best_result = {'start': None, 'end': None, 'params': None, 'final_value': -1}
all_results = []
over_16x_results = []

# === 滑动窗口遍历 + 进度条 + 定时保存 ===
dates = df.index
total_steps = (len(dates) - window_size) * len(param_grid)
progress = tqdm(total=total_steps, desc="⏳ Running Backtests")

last_save_time = time.time()

for i in range(len(dates) - window_size):
    start_date = dates[i]
    end_date = dates[i + window_size - 1]
    window_df = df.loc[start_date:end_date].copy()

    for (macd_fast, macd_slow, macd_signal, rsi_window, rsi_buy, rsi_sell) in param_grid:
        if macd_fast >= macd_slow:
            progress.update(1)
            continue
        try:
            result = run_macd_rsi_strategy(
                window_df.copy(),
                initial_cash=initial_cash,
                macd_fast=macd_fast,
                macd_slow=macd_slow,
                macd_signal=macd_signal,
                rsi_window=rsi_window,
                rsi_buy=rsi_buy,
                rsi_sell=rsi_sell,
                save_plots=False  # ✅ 关闭图像绘制
            )

            final_value = result['final_value']
            record = {
                'Start_Date': start_date.date(),
                'End_Date': end_date.date(),
                'MACD_Fast': macd_fast,
                'MACD_Slow': macd_slow,
                'MACD_Signal': macd_signal,
                'RSI_Window': rsi_window,
                'RSI_Buy': rsi_buy,
                'RSI_Sell': rsi_sell,
                'Final_Value': final_value,
                'Annual_Return': result['annual_return'],
                'Sharpe': result['sharpe_ratio'],
                'Max_Drawdown': result['max_drawdown']
            }
            all_results.append(record)
            if final_value >= 160000:
                over_16x_results.append(record)
            if final_value > best_result['final_value']:
                best_result.update({
                    'start': start_date,
                    'end': end_date,
                    'params': {
                        'macd_fast': macd_fast,
                        'macd_slow': macd_slow,
                        'macd_signal': macd_signal,
                        'rsi_window': rsi_window,
                        'rsi_buy': rsi_buy,
                        'rsi_sell': rsi_sell
                    },
                    'final_value': final_value,
                    'annual_return': result['annual_return'],
                    'sharpe_ratio': result['sharpe_ratio'],
                    'max_drawdown': result['max_drawdown']
                })
        except Exception as e:
            pass
        progress.update(1)

    # 定时保存（每100窗口 或 5分钟）
    if (i + 1) % 100 == 0 or (time.time() - last_save_time > 300):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_df = pd.DataFrame(all_results)
        temp_df.to_csv(f'{save_path}temp_results_up_to_{i+1}_{timestamp}.csv', index=False)
        last_save_time = time.time()

progress.close()

# === 保存最终结果 ===
pd.DataFrame(all_results).to_csv(f'{save_path}all_3month_strategies.csv', index=False)
pd.DataFrame(over_16x_results).to_csv(f'{save_path}explosive_over_16x.csv', index=False)
pd.DataFrame([{
    'Start_Date': best_result['start'].date(),
    'End_Date': best_result['end'].date(),
    'Final_Value': best_result['final_value'],
    'Annual_Return': best_result['annual_return'],
    'Sharpe': best_result['sharpe_ratio'],
    'Max_Drawdown': best_result['max_drawdown'],
    **best_result['params']
}]).to_csv(f'{save_path}explosive_strategy_result.csv', index=False)

print("\n✅ All files saved to /mnt/data/backtest_results/")

import subprocess
subprocess.run(['python3', '/mnt/data/upload_all_to_s3.py'])

