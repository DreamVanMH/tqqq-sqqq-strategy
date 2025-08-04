import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

def run_macd_rsi_strategy(df, 
                          initial_cash=10000, 
                          macd_fast=12, 
                          macd_slow=26, 
                          macd_signal=9, 
                          rsi_window=14, 
                          rsi_buy=30, 
                          rsi_sell=70,
                          save_plots=False,
                          verbose=True):  # ✅ 添加控制打印输出的参数

    df = df.copy()

    # === 计算 MACD 指标 ===
    df['EMA_fast'] = df['Close'].ewm(span=macd_fast, adjust=False).mean()
    df['EMA_slow'] = df['Close'].ewm(span=macd_slow, adjust=False).mean()
    df['MACD'] = df['EMA_fast'] - df['EMA_slow']
    df['Signal'] = df['MACD'].ewm(span=macd_signal, adjust=False).mean()

    # === 计算 RSI 指标 ===
    delta = df['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=rsi_window).mean()
    avg_loss = loss.rolling(window=rsi_window).mean()
    rs = avg_gain / avg_loss
    df['RSI'] = 100 - (100 / (1 + rs))

    # === 生成买入/卖出信号 ===
    df['Buy_Signal'] = (df['MACD'] > df['Signal']) & (df['RSI'] < rsi_buy)
    df['Sell_Signal'] = (df['MACD'] < df['Signal']) & (df['RSI'] > rsi_sell)

    # === 回测逻辑 ===
    position = 0
    cash = initial_cash
    shares = 0
    portfolio_values = []

    for i in range(len(df)):
        price = df['Close'].iloc[i]

        if df['Buy_Signal'].iloc[i] and position == 0:
            shares = cash / price
            cash = 0
            position = 1
        elif df['Sell_Signal'].iloc[i] and position == 1:
            cash = shares * price
            shares = 0
            position = 0

        portfolio_value = cash + shares * price
        portfolio_values.append(portfolio_value)

    df['Strategy'] = portfolio_values
    df['BuyHold'] = initial_cash * (df['Close'] / df['Close'].iloc[0])

    # === 绩效评估 ===
    returns = df['Strategy'].pct_change().dropna()
    final_value = df['Strategy'].iloc[-1]
    days = (df.index[-1] - df.index[0]).days
    annual_return = (final_value / initial_cash) ** (365.0 / days) - 1
    annual_volatility = returns.std() * np.sqrt(252)
    sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252)
    rolling_max = df['Strategy'].cummax()
    drawdown = df['Strategy'] / rolling_max - 1
    max_drawdown = drawdown.min()

    # ✅ 控制是否打印输出
    if verbose:
        print("\n=== Strategy Performance ===")
        print(f"Initial Capital      : ${initial_cash:.2f}")
        print(f"Final Portfolio Value: ${final_value:.2f}")
        print(f"Annual Return        : {annual_return:.2%}")
        print(f"Annual Volatility    : {annual_volatility:.2%}")
        print(f"Sharpe Ratio         : {sharpe_ratio:.2f}")
        print(f"Max Drawdown         : {max_drawdown:.2%}")

    # === 可选图像绘制 ===
    if save_plots:
        output_dir = "/mnt/data/backtest_results"
        os.makedirs(output_dir, exist_ok=True)

        # 策略 vs BuyHold 图
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['Strategy'], label='MACD + RSI Strategy')
        plt.plot(df.index, df['BuyHold'], label='Buy & Hold', linestyle='--')
        plt.title("MACD + RSI Strategy vs Buy & Hold")
        plt.xlabel("Date")
        plt.ylabel("Portfolio Value ($)")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'tqqq_strategy_vs_buyhold.png'))
        plt.close()

        # 买卖信号图
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['Close'], label='Close Price', alpha=0.7)
        plt.plot(df.index[df['Buy_Signal']], df['Close'][df['Buy_Signal']], '^', markersize=8, color='g', label='Buy Signal')
        plt.plot(df.index[df['Sell_Signal']], df['Close'][df['Sell_Signal']], 'v', markersize=8, color='r', label='Sell Signal')
        plt.title("Buy/Sell Signals on Close Price")
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'tqqq_signals.png'))
        plt.close()

    return {
        "df": df,
        "final_value": final_value,
        "annual_return": annual_return,
        "annual_volatility": annual_volatility,
        "sharpe_ratio": sharpe_ratio,
        "max_drawdown": max_drawdown
    }
