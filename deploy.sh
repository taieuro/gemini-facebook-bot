#!/bin/bash

# --- HƯỚNG DẪN SỬ DỤNG ---
#
# ./deploy.sh "Nội dung ghi chú" <số phút> <on/off>
#
# Tham số:
#   $1: Nội dung ghi chú cho lần cập nhật (bắt buộc, đặt trong dấu "")
#   $2: Số phút để bot tự động hoạt động trở lại (bắt buộc, chỉ nhập số)
#   $3: Bật hoặc tắt tính năng "Human Takeover" (tùy chọn, nhập "on" hoặc "off". Mặc định là "on")
#
# Ví dụ 1: Cập nhật code, bot tự mở lại sau 30 phút, bật tính năng takeover
#   ./deploy.sh "Sửa lỗi chính tả" 30
#
# Ví dụ 2: Chỉ thay đổi thời gian chờ thành 60 phút, không cập nhật code
#   ./deploy.sh "Cập nhật thời gian chờ" 60
#
# Ví dụ 3: Tắt hoàn toàn tính năng takeover
#   ./deploy.sh "Tắt tính năng takeover" 30 off
#

# --- PHẦN CODE XỬ LÝ ---

# Kiểm tra xem các tham số bắt buộc đã được cung cấp chưa
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "❌ Lỗi: Vui lòng cung cấp đầy đủ thông tin."
  echo "Cách dùng: ./deploy.sh \"Nội dung cập nhật\" <số phút> [on/off]"
  echo "Ví dụ:    ./deploy.sh \"Cập nhật KNOWLEDGE_BASE\" 30"
  exit 1
fi

# Gán các tham số vào biến để code dễ đọc hơn
COMMIT_MESSAGE="$1"
RESUME_MINUTES="$2"
TAKEOVER_MODE=${3:-on} # Nếu không có tham số thứ 3, mặc định là "on"

# Chuyển đổi on/off thành true/false
if [ "$TAKEOVER_MODE" == "on" ]; then
  TAKEOVER_ENABLED="true"
  echo "✅ Tính năng 'Human Takeover' sẽ được BẬT."
else
  TAKEOVER_ENABLED="false"
  echo "🅾️  Tính năng 'Human Takeover' sẽ được TẮT."
fi

echo "🚀 Bắt đầu quá trình cập nhật..."
echo "------------------------------------"

# Bước 1: Cập nhật các cài đặt (secrets) trên Fly.io
echo "⚙️  Đang cập nhật cài đặt bot trên Fly.io..."
fly secrets set HUMAN_TAKEOVER_ENABLED="$TAKEOVER_ENABLED" -q
fly secrets set BOT_RESUME_MINUTES="$RESUME_MINUTES" -q
echo "    - Tự động dừng khi nhân viên chat: $TAKEOVER_ENABLED"
echo "    - Tự động mở lại sau: $RESUME_MINUTES phút"

# Bước 2: Đóng gói và gửi code lên GitHub
echo "📦 Đang đóng gói và gửi code lên GitHub..."
git add .
git commit -m "$COMMIT_MESSAGE"
git push origin main

# Bước 3: Triển khai phiên bản mới lên Fly.io
echo "✈️  Đang triển khai phiên bản mới lên Fly.io (quá trình này mất vài phút)..."
fly deploy

echo "------------------------------------"
echo "✅ Cập nhật và triển khai hoàn tất!"
