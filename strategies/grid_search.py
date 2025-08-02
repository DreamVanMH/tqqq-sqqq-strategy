import pandas as pd
import itertools
from macd_rsi_strategy import run_macd_rsi_strategy

def grid_search_macd_rsi(df, initial_cash=10000):
    # 定义搜索空间
    macd_fast_list = [8, 10, 12]
    macd_slow_list = [20, 24, 26]
    macd_signal_list = [6, 8, 9]
    rsi_window_list = [10, 14]
    rsi_buy_threshold_list = [30, 32]
    rsi_sell_threshold_list = [70, 72]

    results = []

    # 所有组合的笛卡尔积
    for macd_fast, macd_slow, macd_signal, rsi_window, rsi_buy, rsi_sell in itertools.product(
        macd_fast_list, macd_slow_list, macd_signal_list,
        rsi_window_list, rsi_buy_threshold_list, rsi_sell_threshold_list):

        if macd_fast >= macd_slow:
            continue  # 快线必须小于慢线

        try:
            result = run_macd_rsi_strategy(
                df,
                initial_cash=initial_cash,
                macd_fast=macd_fast,
                macd_slow=macd_slow,
                macd_signal=macd_signal,
                rsi_window=rsi_window,
                rsi_buy=rsi_buy,
                rsi_sell=rsi_sell
            )

            results.append({
                "MACD_Fast": macd_fast,
                "MACD_Slow": macd_slow,
                "MACD_Signal": macd_signal,
                "RSI_Window": rsi_window,
                "RSI_Buy": rsi_buy,
                "RSI_Sell": rsi_sell,
                "Final_Value": result["final_value"],
                "Sharpe": result["sharpe_ratio"],
                "Annual_Return": result["annual_return"],
                "Max_Drawdown": result["max_drawdown"],
            })

        except Exception as e:
            print(f"Error with combination {macd_fast}-{macd_slow}-{macd_signal}, {rsi_window}, {rsi_buy}-{rsi_sell}: {e}")
            continue

    return pd.DataFrame(results)
