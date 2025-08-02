
# tqqq-sqqq-strategy
Python project for backtesting and live-trading TQQQ & SQQQ ETF strategies using **Interactive Brokers (IBKR)** API.  
Supports technical indicator optimization (MACD + RSI), parallel backtesting, and cloud deployment on AWS.

# TQQQ & SQQQ ETF Strategy Backtesting and IBKR Trading 🚀

This project is a Python-based trading system designed for:
- 📈 Backtesting leveraged Nasdaq ETF strategies (TQQQ & SQQQ)
- 🧠 Optimizing MACD + RSI logic with grid search and sliding windows
- 🛠️ Executing **automated live and paper trades via IBKR API (`ib_insync`)**
- ☁️ Running large-scale backtests in parallel on **AWS EC2 + EBS + S3**
- 📊 Visualizing buy/sell signals and performance vs. Buy&Hold

---

## ✅ Features

- 💡 **Strategy**: MACD crossover with RSI filter
- 🔍 **Optimization**: Grid search for ideal indicator thresholds
- 🔁 **Rolling Windows**: Find 3-month high-growth strategies
- 📊 **Plotting**: Buy/sell signal chart + strategy vs. Buy&Hold performance
- 🔌 **IBKR API Integration**: Full support for paper and real trading accounts
- ⚙️ **Parallel Backtesting**: Using `multiprocessing` to accelerate testing
- ☁️ **Cloud Ready**: Deployed on AWS with EC2, EBS volumes, and S3 syncing
- 🧱 **Modular Design**: Easily extend to new tickers, strategies, or brokers

---

## 📡 Broker: Interactive Brokers (IBKR)

This project uses **Interactive Brokers** as the trading platform, fully supporting:
- ✅ Paper Trading
- ✅ Real Account Execution
- ✅ Connection via `ib_insync` (Python interface for TWS/IB Gateway)

---

## 📁 Folder Structure

```
.
├── strategies/
│   ├── macd_rsi_strategy.py             # Core strategy logic
│   ├── grid_search.py                   # Grid search engine
│   ├── find_explosive_3month_strategy_parallel.py  # Parallel backtest runner
│   └── ...
├── broker/
│   └── ibkr_trading.py                  # IBKR API connection & trade execution
├── data/                                # Raw ETF price data
├── backtest_results/                    # Output metrics and visualizations
├── upload_all_to_s3.py                  # S3 batch uploader
├── requirements.txt
├── README.md
```

---

## ▶️ Run Examples

```bash
# Grid search over full dataset (TQQQ)
python run_grid_search.py

# 3-month rolling strategy scan (parallelized)
python strategies/find_explosive_3month_strategy_parallel.py

# Upload results to S3
python upload_all_to_s3.py
```

---

## ☁️ AWS Cloud Setup

- EC2 Spot instance (e.g., `c5.4xlarge`) with 16 vCPUs
- External EBS volume for persistent storage (`/mnt/data`)
- Strategy results auto-saved to `.csv` and `.png`
- Periodic backup to Amazon S3

---

## 🔐 Disclaimer

- This project is for research and educational purposes only.
- No financial advice is provided.
- Backtest results may not reflect real-world performance.

---

## 📬 Contact

For collaboration or questions, please open an issue or submit a pull request.
