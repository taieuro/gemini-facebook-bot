#!/bin/bash

# ==============================================================================
# --- KHUNG CẬP NHẬT PAGE ACCESS TOKENS ---
#
# Hướng dẫn: 
# 1. Dán chuỗi JSON mới của bạn vào giữa hai dấu nháy đơn ('').
# 2. Nếu bạn KHÔNG cần cập nhật token trong lần chạy này, hãy để trống: PAGE_TOKENS_JSON=''
#
PAGE_TOKENS_JSON=''
#
# ==============================================================================


# --- HƯỚNG DẪN SỬ DỤNG LỆNH ---
#
# ./deploy.sh "Nội dung ghi chú" <số phút> <on/off>
#
# Tham số:
#   $1: Nội dung ghi chú cho lần cập nhật (bắt buộc, đặt trong dấu "")
#   $2: Số phút để bot tự động hoạt động trở lại (bắt buộc, chỉ nhập số)
#   $3: Bật hoặc tắt tính năng "Human Takeover" (tùy chọn, nhập "on" hoặc "off". Mặc định là "on")
#

# --- PHẦN CODE XỬ LÝ (Không cần chỉnh sửa phần dưới này) ---

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
TAKEOVER_MODE=${3:-on}

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
fly secrets set HUMAN_TAKEOVER_ENABLED="$TAKEOVER_ENABLED"
fly secrets set BOT_RESUME_MINUTES="$RESUME_MINUTES"
echo "    - Tự động dừng khi nhân viên chat: $TAKEOVER_ENABLED"
echo "    - Tự động mở lại sau: $RESUME_MINUTES phút"

# Bước 1.5: Cập nhật chuỗi JSON nếu có
if [ -n "$PAGE_TOKENS_JSON" ]; then
  echo "🔑 Đang cập nhật chuỗi Page Access Tokens..."
  fly secrets set PAGE_TOKENS_JSON="$PAGE_TOKENS_JSON"
  echo "    - Đã gửi chuỗi JSON mới lên server."
else
  echo "🔑 Không có chuỗi JSON mới, bỏ qua bước cập nhật token."
fi

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
