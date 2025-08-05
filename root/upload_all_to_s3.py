import os
import boto3
from pathlib import Path
from datetime import datetime

# === 设置 ===
bucket_name = 'tqqq-backtest'
upload_targets = {
    '/mnt/data/backtest_results': 'tqqq/',
    '/mnt/data/backtest_results_sqqq': 'sqqq/',
    '/mnt/data/strategies': 'strategies/',
    '/mnt/data/root': 'root/',
    '/mnt/data/broker': 'broker/'
}

# === 获取今天的日期作为子路径 ===
date_prefix = datetime.today().strftime('%Y-%m-%d')

# === 创建 S3 客户端 ===
s3 = boto3.client('s3')

# === 上传函数 ===
def upload_folder_to_s3(local_dir: Path, s3_prefix: str):
    upload_count = 0
    fail_count = 0
    failed_files = []

    for file in local_dir.rglob('*'):
        if file.is_file():
            s3_key = f'{s3_prefix}{file.relative_to(local_dir)}'.replace('\\', '/')
            try:
                print(f'☁️ Uploading {file} → {s3_key}')
                s3.upload_file(str(file), bucket_name, s3_key)
                upload_count += 1
            except Exception as e:
                print(f'⚠️ Failed to upload {file}: {e}')
                failed_files.append((file, str(e)))
                fail_count += 1

    return upload_count, fail_count, failed_files

# === 主流程 ===
total_uploaded = 0
total_failed = 0
all_failed_files = []

for local_path, s3_base_prefix in upload_targets.items():
    folder = Path(local_path)
    if not folder.exists():
        print(f'⚠️ 跳过：本地路径不存在：{folder}')
        continue

    s3_prefix = f'{s3_base_prefix}{date_prefix}/'
    print(f'📁 Uploading folder: {folder} → s3://{bucket_name}/{s3_prefix}')

    uploaded, failed, failed_files = upload_folder_to_s3(folder, s3_prefix)
    total_uploaded += uploaded
    total_failed += failed
    all_failed_files.extend(failed_files)

print(f'\n✅ Upload complete. Total uploaded: {total_uploaded}, Failed: {total_failed}')

# === 写入失败日志 ===
if total_failed > 0:
    log_path = Path(f'/mnt/data/root/upload_failed_log_{date_prefix}.txt')
    with log_path.open('w') as log_file:
        for f, err in all_failed_files:
            line = f'{f}: {err}\n'
            log_file.write(line)
    print(f'❌ Failed file log saved to: {log_path}')
