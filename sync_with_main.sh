#!/bin/bash

cd /mnt/data || exit

echo "🔄 Fetching latest remote changes..."
git fetch origin main

echo "🔁 Merging origin/main into current branch..."
git merge origin/main

echo "✅ Done. You are now up to date with main!"
