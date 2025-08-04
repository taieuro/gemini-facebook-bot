#!/bin/bash
echo "🚀 Bắt đầu quá trình cập nhật..."
git add .
git commit -m "$1"
git push origin main
fly deploy
echo "✅ Cập nhật hoàn tất!"