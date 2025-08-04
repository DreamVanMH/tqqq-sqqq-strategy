import yfinance as yf
import os

# 下载 TQQQ 历史数据（从 2014-01-01 到今天）
ticker = "TQQQ"
start_date = "2014-01-01"
end_date = None  # 默认抓到今天（建议用 None）

print(f"Downloading {ticker} data from {start_date} to {end_date}...")

df = yf.download(ticker, start=start_date, end=end_date)

# ✅ 保存到 EC2 挂载盘
save_path = "/mnt/data/data/sqqq.csv"
os.makedirs(os.path.dirname(save_path), exist_ok=True)

df.to_csv(save_path)
print(f"✅ TQQQ 历史数据已保存到：{save_path}")
