#!/bin/bash

# ==============================================================================
# --- KHUNG CẬP NHẬT PAGE ACCESS TOKENS ---
#
# Hướng dẫn: 
# 1. Dán chuỗi JSON mới của bạn vào giữa hai dấu nháy đơn ('').
# 2. Nếu bạn KHÔNG cần cập nhật token trong lần chạy này, hãy để trống: PAGE_TOKENS_JSON=''
#
PAGE_TOKENS_JSON='{
    "979089732297732":"EAARn8FHmZBuUBPCgD9PjxZAzGARu2vyo6YqtCvDtWdjIdFjaQxhQlBk91HST0r3nDuVZCdSu4PwZBKSSvN5KayxQaxHEfLfOpBmlCbr1N6E10ocAPxRzc9K5NufZCaeKzXNXjU1dYOyP0FfWnH7KcwzhWC1q1fYBpgiCW959lqoKa9YdCIKaSlV00LPmcHjhXcaGvdoQd2P5LTVrE7kqqJ8pctQZDZD",
    "103852944432227":"EAARn8FHmZBuUBPBUd4MqrBLP37mCoUZCHGZCdQc3xeOW73aT0ST4ZCnTP0ZAF6OZBduQQmLzUUhtRi1EyivEZCnZClYHNVMqMU3zSlDP4WZB6bSHG0GABKJIcUKzFa6u7MeW3HupImZCjKOu01dVGWvopkHEuzan5e2uGD6LZATN15kFj6xyVfUMNXAQCICIylZBrNkU1RZB8zdK0N0zg2H6bn9bZAgq6G",
    "523679261475958":"EAARn8FHmZBuUBPHLm8ZBrBZB6hCg1KQEnlxV7tMI3ZAZAdSU56ZAIv5PeyakQjk0N1sWSmziYCOO0heRCI38Gnc3vFuGNTZAWNEu1FDTWoOtzCa2Xb2Iv5LfUOBvByGM0lZA5YHF2ZBWZAQE7FxZA4N3aLc3zkG583hEFm5ZC3ak8oVuyC6JaUkuE2ehn9ZAjuWt3MfoagNiGAVbu6n0IsyUqvOX8rAULOwZDZD",
    "103069574791731":"EAARn8FHmZBuUBPAcwykq8zRffGZBD8ryPAHSqefMvpfwZBHT5GjUQ79TM7SFnChUWhKoiDJykqpM1forZCK17FDv21wAdxVUaeQ3pnxGmxZBx5ZAqMx3bqsc9wjXJJwdEuUuAnkPqf51BEFpx6oRmAkdmwDC5tD6u0OkUmBfYuqP94rYmhshjUNRKTCrlgZA3fgnmUFLw5PjbANZBltKOvwsidZCk",
    "2404892766250369":"EAARn8FHmZBuUBPJpzA0qJ1lJKcAi4VjQBIfmNOqEDQ8RNDAvNvbUXnTvsDBewUQSjktpDbRrn3YzlGoEA5rOUijwhLjAZBCQPk80Jv9vIV5DgFhMsceOk00ZCdZC8ZC2JL7kuooG4YqjhyM3758gABjq51rYa6KZCsZC46bczDntcZAc8ZCt1pscBZAC1pmha6lXYnVonK9Q2N7Rmsh1ZAgToLo4KYk4AZDZD",
    "722624244804439":"EAARn8FHmZBuUBPORTK9YsHUZBt1PbCtUxgD1BEVddai64FUkkm9CBDTdPRDsziCOSeBZBkmNsO85OoogGauMyQ62uZCA9K3hh1HKwvfDWnXDUnp6zZCQc9nF0HrpTmGeeBQsTq9HdfHiPkGvjUyCgDXm2YVaMCIfYCZCrjzTDkZB3DYjvA4teBWDJQvaiYPCkk3OZCHMFMIuuFGhhNZAYsj17ZCCZCe9wZDZD",
    "1994560940650945":"EAARn8FHmZBuUBPGJY7PpgrpzV3FFuhcZCyU9IYzVXklyxRHQQbASoGTPMdOrSjSjXPavZBc3CiwP8htoej6NvAnlieMtvU2ZBLVjC2qF38ZAjZBZCUvhJ9mGVyI8zw817M0PGvqfTv1b7wOU0CZBIAIeytZB5Ky73wlgfOfzvu1mZBilmmDyqoO8hQTPf9OxQgVyJuj0JZBlgfmPdLdvr7Rh2Vld9Qe2QZDZD",
    "793488794318691":"EAARn8FHmZBuUBPCcDqmla7VJwCXJv74ZBBFl2qDFFrPjLeV6exP1iiQizTBv6ZApro4xmauPw2rzOymz0ZBjXKE0J8720ehg27gOHTZCD6kSctmiF8DHXDBsi4mvroMVGB6kUmBii917fJrIyFZAoqq3bSIZB9VpWw7UC3w3PPSDqHmBeZCoDMWwkhfaSgkrD4GzIPBM4VOTFOCmk7EMdtN1epx5hwZDZD",
    "2439206186094635":"EAARn8FHmZBuUBPCNmM7kjA6ayuHGQkpZAazqmJ7W8n2oyhOZAIUFWfnbNSiCKQiEPTcd8ICvSlvfEnk6yH71uaRv8nUzDQ70tfkvW3zDMCMZAjywDcfVGCmqRdvn129ZAhN9LDbTaabaqLCQnurfj8M6xMgaXtZAIGxG3VSwVABJ7KTVfre1MH4OMfgZC9B0HQBF8aq4S1YfJ1KZA5r6daJCVyZC91AZDZD",
    "103528334464837":"EAAauFugZBx7IBPLJcea9SGKwzM8VeK1YR3q3GVcJKaEhBknGjQolu5K9TARjJvRz9xrk4eO2bVtDgRISKsQ24ZAgvZAbsjyhg5ydJCx9m7LW33smkb5YQZCp9gXSF3REeoGszLq6Tf2bZBv1x1Sl5v6KDZAW8uOzG4BsOsT7ZCKp9YXdkdIrJvk6XaLQf3ZAE0RTJ0P7w1afVvEMBsSNa7Cd",
    "111068640386115":"EAAauFugZBx7IBPA2UzOCRKrZBMNNgqULs2cFYIkyEV6QZBnKvZB0iDiuAd9qAzBPDvgsto0ipBHTMZBpAuimDPyMc7YJQbqF1O7O6vkzLkZAFTaF2oZA2ZBooM8kB4sLzXD9MQsy4uj2YiTTEeAcZBKYdu75VcPaK9LUpwa5TOVL9ZAmuvah9nCknDYHZAw57oQ0voxA09we36Jv6jyxCrJ8ORS"
}'
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
