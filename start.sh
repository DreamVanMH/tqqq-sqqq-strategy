#!/bin/bash

# 自动挂载数据盘
echo "Mounting data volume to /mnt/data..."
sudo mkdir -p /mnt/data
sudo mount /dev/nvme1n1 /mnt/data
sudo chown ubuntu:ubuntu /mnt/data

echo "Activating virtual environment..."
source ~/.venv/bin/activate

echo "Running setup script to install packages, check resume point, and upload existing results..."
python3 /mnt/data/root/setup_venv_and_run.py
