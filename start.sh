#!/bin/bash

echo "🔧 [1/6] Mounting volume to /mnt/data..."
sudo mkdir -p /mnt/data
sudo mount | grep /mnt/data || sudo mount /dev/nvme1n1 /mnt/data
sudo chown ubuntu:ubuntu /mnt/data

echo "📦 [2/6] Updating system & installing dependencies..."
sudo apt update
sudo apt install -y python3-venv python3-pip

echo "🌱 [3/6] Creating virtual environment at /mnt/data/myenv (if not exists)..."
if [ ! -d "/mnt/data/myenv" ]; then
  python3 -m venv /mnt/data/myenv
fi

echo "⚡ [4/6] Activating virtual environment..."
source /mnt/data/myenv/bin/activate

echo "📚 [5/6] Installing Python packages from requirements.txt..."
pip install --upgrade pip
pip install --break-system-packages -r /mnt/data/root/requirements.txt

echo "🚀 [6/6] Running strategy launcher script..."
python3 /mnt/data/root/setup_venv_and_run.py
