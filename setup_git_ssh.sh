#!/bin/bash

# === 自动恢复 GitHub SSH 认证配置（含公钥） ===

KEY_PATH="/mnt/data/id_ed25519"
CONFIG_PATH="$HOME/.ssh/config"

# 1. 确保 ~/.ssh 目录存在
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# 2. 写入 SSH config（自动识别 GitHub + 私钥路径）
cat > "$CONFIG_PATH" <<EOF
Host github.com
  HostName github.com
  User git
  IdentityFile $KEY_PATH
EOF

# 3. 设置权限
chmod 600 "$KEY_PATH"
chmod 600 "$CONFIG_PATH"

# 4. 自动恢复公钥（如果不存在）
if [ ! -f "$KEY_PATH.pub" ]; then
  echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIASlAc6Fi4G3KcS3KOlfib6s6lXLmSwzaXTrpSfE/yTP yinglu522@gmail.com" > "$KEY_PATH.pub"
  chmod 644 "$KEY_PATH.pub"
  echo "🛠️ 公钥 id_ed25519.pub 已自动恢复"
fi

# 5. 测试连接
ssh -T git@github.com

# 6. 提示信息
echo -e "\n✅ SSH config restored. Git push should now work without password."
