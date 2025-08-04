#!/bin/bash

# 设置变量
BRANCH=$(git branch --show-current)
MESSAGE=${1:-"Update from AWS"}

# 显示当前操作信息
echo "🚀 CurrentBranch: $BRANCH"
echo "📝 Message: $MESSAGE"

# 添加全部改动（包括新增、修改、删除）
git add .

# 创建提交
git commit -m "$MESSAGE"

# 推送到远程
git push

echo "✅ 已推送到 GitHub: $BRANCH"
