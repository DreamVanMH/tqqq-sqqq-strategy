import pandas as pd
import matplotlib.pyplot as plt
import os
from macd_rsi_strategy import run_macd_rsi_strategy

# ====== 1. 文件路径设定 ======
grid_results_path = '/mnt/data/backtest_results/tqqq_grid_search_results_20250723_235205.csv'
raw_data_path = '/mnt/data/data/tqqq.csv'
output_dir = '/mnt/data/backtest_results'
os.makedirs(output_dir, exist_ok=True)

# ====== 2. 加载并清洗数据 ======
df = pd.read_csv(grid_results_path)
top_strategies = df.sort_values(by='Sharpe', ascending=False).head(5)

price_df = pd.read_csv(raw_data_path)
#price_df.columns = price_df.columns.str.strip().str.lower()
price_df['Date'] = pd.to_datetime(price_df['Date'])
price_df.set_index('Date', inplace=True)

# ====== 3. 绘图 Top 5 策略结果 ======
for i, row in top_strategies.iterrows():
    macd_fast = int(row['MACD_Fast'])
    macd_slow = int(row['MACD_Slow'])
    macd_signal = int(row['MACD_Signal'])
    rsi_window = int(row['RSI_Window'])
    rsi_buy = float(row['RSI_Buy'])
    rsi_sell = float(row['RSI_Sell'])

    result = run_macd_rsi_strategy(price_df.copy(),
                                   initial_cash=10000,
                                   macd_fast=macd_fast,
                                   macd_slow=macd_slow,
                                   macd_signal=macd_signal,
                                   rsi_window=rsi_window,
                                   rsi_buy=rsi_buy,
                                   rsi_sell=rsi_sell)

    df_result = result['df']
    buy_signals = df_result[df_result['Signal'] == 1]
    sell_signals = df_result[df_result['Signal'] == -1]

    # === 图 1: Buy/Sell 信号图 ===
    plt.figure(figsize=(12, 6))
    plt.plot(df_result.index, df_result['Close'], label='Close Price', alpha=0.7)
    plt.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', label='Buy Signal')
    plt.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', label='Sell Signal')
    plt.title(f'[Strategy {i}] Buy/Sell Signals')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/strategy_{i}_signals.png')
    plt.close()

    # === 图 2: 策略 vs Buy&Hold 图 ===
    plt.figure(figsize=(12, 6))
    plt.plot(df_result.index, df_result['Strategy'], label='MACD + RSI Strategy')
    plt.plot(df_result.index, df_result['BuyHold'], label='Buy & Hold', linestyle='--', color='orange')
    plt.title(f'[Strategy {i}] MACD + RSI Strategy vs Buy & Hold')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value ($)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/strategy_{i}_vs_buyhold.png')
    plt.close()

# ====== 4. 打印 Top 5 策略信息 ======
print("\n=== Top 5 Strategies ===")
print(top_strategies[['MACD_Fast', 'MACD_Slow', 'MACD_Signal',
                      'RSI_Window', 'RSI_Buy', 'RSI_Sell',
                      'Final_Value', 'Sharpe', 'Annual_Return', 'Max_Drawdown']])

# ====== 5. 附加测试：尝试实现3个月暴涨策略 ======
print("\n=== Testing Short-Term Extreme Strategy ===")

test_result = run_macd_rsi_strategy(price_df.tail(63).copy(),  # 近3个月数据
                                    initial_cash=10000,
                                    macd_fast=3,
                                    macd_slow=9,
                                    macd_signal=2,
                                    rsi_window=6,
                                    rsi_buy=25,
                                    rsi_sell=60)

df_test = test_result['df']
print("Final Value:", df_test['Strategy'].iloc[-1])
print("Buy & Hold :", df_test['BuyHold'].iloc[-1])
