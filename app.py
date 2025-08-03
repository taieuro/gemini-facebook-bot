# --- Bước 1: Nhập các thư viện cần thiết ---
import os
from flask import Flask, request
import requests
from dotenv import load_dotenv
import google.generativeai as genai # Thư viện để giao tiếp với Gemini

# --- Bước 2: Tải các biến môi trường từ file .env ---
# Thao tác này sẽ lấy các mã bí mật bạn đã lưu trong file .env
# một cách an toàn, không để lộ ra ngoài code.
load_dotenv()
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# --- Bước 3: Cấu hình mô hình Gemini ---
# Sử dụng API Key của bạn để xác thực với Google.
# Khai báo mô hình bạn muốn sử dụng, ở đây là 'gemini-2.5-flash'.
try:
    genai.configure(api_key=GEMINI_API_KEY)
    # DÒNG QUAN TRỌNG: Khai báo sử dụng model gemini-2.5-flash
    model = genai.GenerativeModel('gemini-2.5-flash')
    print("Đã cấu hình Gemini với model 'gemini-2.5-flash' thành công!")
except Exception as e:
    print(f"Lỗi khi cấu hình Gemini: {e}")
    model = None

# --- Bước 4: Khởi tạo ứng dụng Flask ---
# Đây là "trái tim" của server sẽ lắng nghe tín hiệu từ Facebook
app = Flask(__name__)

# --- Bước 5: Xây dựng hàm gửi tin nhắn trả lời qua Facebook ---
def send_message(recipient_id, message_text):
    """Hàm này dùng để gửi tin nhắn văn bản đến người dùng Facebook."""
    print(f"Đang gửi tin nhắn tới {recipient_id}: {message_text}")
    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        },
        "messaging_type": "RESPONSE" # Tuân thủ chính sách của Facebook
    }
    # Gửi yêu cầu POST đến API của Facebook để gửi tin nhắn đi
    r = requests.post("https://graph.facebook.com/v19.0/me/messages", params=params, headers=headers, json=data)
    if r.status_code != 200:
        print(f"Lỗi khi gửi tin nhắn: {r.status_code} {r.text}")

# --- Bước 6: Xây dựng hàm lấy câu trả lời từ Gemini ---
def get_gemini_response(prompt):
    """Hàm này gửi yêu cầu đến Gemini và nhận lại câu trả lời."""
    # Kiểm tra xem model đã được cấu hình thành công chưa
    if not model:
        return "Lỗi: Mô hình Gemini chưa được cấu hình."
    try:
        # Gửi prompt (tin nhắn của người dùng) đến Gemini
        response = model.generate_content(prompt)
        # Trả về phần text trong câu trả lời của Gemini
        return response.text
    except Exception as e:
        print(f"Lỗi khi gọi API Gemini: {e}")
        return "Xin lỗi, tôi đang gặp một chút sự cố. Vui lòng thử lại sau."

# --- Bước 7: Tạo Webhook Endpoint ---
# Endpoint này có 2 nhiệm vụ:
# 1. Xác thực webhook với Facebook (khi nhận yêu cầu GET)
# 2. Nhận tin nhắn từ người dùng và xử lý (khi nhận yêu cầu POST)
@app.route('/', methods=['GET', 'POST'])
def webhook():
    # Nhiệm vụ 1: Xác thực (chỉ xảy ra một lần khi cấu hình)
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        if token_sent == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return 'Invalid verification token', 403

    # Nhiệm vụ 2: Nhận tin nhắn và xử lý
    if request.method == 'POST':
        data = request.get_json()
        if data["object"] == "page":
            for entry in data["entry"]:
                for messaging_event in entry["messaging"]:
                    # Nếu có tin nhắn văn bản được gửi đến
                    if messaging_event.get("message"):
                        sender_id = messaging_event["sender"]["id"]      # Lấy ID của người gửi
                        message_text = messaging_event["message"]["text"] # Lấy nội dung tin nhắn

                        # Gửi tin nhắn của người dùng đến Gemini để lấy câu trả lời
                        gemini_answer = get_gemini_response(message_text)

                        # Gửi câu trả lời của Gemini về cho người dùng
                        send_message(sender_id, gemini_answer)

        return "ok", 200

# --- Bước 8: Chạy server ---
# Dòng này đảm bảo server chỉ chạy khi bạn thực thi trực tiếp file app.py
if __name__ == '__main__':
    # Chạy server, lắng nghe từ mọi địa chỉ IP trên cổng 5001
    app.run(host='0.0.0.0', port=5001, debug=True)
