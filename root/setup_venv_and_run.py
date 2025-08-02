import os
import subprocess
from pathlib import Path
from datetime import datetime
import pandas as pd

# === Step 1: 创建虚拟环境（如果不存在） ===
venv_path = Path.home() / '.venv'
if not venv_path.exists():
    print(f'📦 Creating virtual environment at {venv_path}...')
    subprocess.run(['sudo', 'apt', 'update'])
    subprocess.run(['sudo', 'apt', 'install', '-y', 'python3.12-venv'])  # 确保安装 venv 模块
    subprocess.run(['python3', '-m', 'venv', str(venv_path)])

# === Step 2: 安装依赖（requirements.txt） ===
pip_path = venv_path / 'bin' / 'pip'
req_path = Path('/mnt/data/root/requirements.txt')
if req_path.exists():
    print('📦 Installing dependencies from requirements.txt...')
    subprocess.run([str(pip_path), 'install', '-r', str(req_path)])
else:
    print('⚠️  requirements.txt not found')

print('\n✅ Environment setup complete. You can now run your strategy script.')

# === Step 3: 判断是否存在中断保存结果（支持 TQQQ + SQQQ） ===
for name in ['sqqq', 'tqqq']:
    try:
        partial_path = Path(f'/mnt/data/backtest_results_{name}/all_3month_strategies_{name}.csv')
        if partial_path.exists():
            df_existing = pd.read_csv(partial_path)
            print(f'📂 Detected previous result file: {partial_path.name}')
            print(f'📊 Previously completed rows for {name.upper()}: {len(df_existing)}')
        else:
            print(f'🆕 No previous result file for {name.upper()}. Full run will be performed.')
    except Exception as e:
        print(f'⚠️ Error reading previous result file for {name.upper()}: {e}')

# === Step 4: 上传结果与策略代码到 S3 ===
print('\n☁️ Uploading results and strategies to S3...')
subprocess.run(['python3', '/mnt/data/root/upload_all_to_s3.py'])

# === Step 5: 写入 backtest_log.txt 日志记录（时间戳） ===
try:
    log_path = Path('/mnt/data/root/backtest_log.txt')
    with open(log_path, 'a') as f:
        f.write(f"[START] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Launched setup and upload\n")
    print(f'📝 Log appended to {log_path}')
except Exception as e:
    print(f'⚠️ Could not write log file: {e}')
