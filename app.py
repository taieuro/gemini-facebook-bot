# --- Bước 1: Nhập các thư viện cần thiết ---
import os
from flask import Flask, request, send_from_directory
import requests
from dotenv import load_dotenv
import google.generativeai as genai

# --- Bước 2: Tải các biến môi trường từ file .env ---
load_dotenv()
# Facebook Tokens
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')
# Gemini API Key
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
# Zalo Tokens
ZALO_ACCESS_TOKEN = os.getenv('ZALO_ACCESS_TOKEN')

# --- Bước 3: Cấu hình mô hình Gemini ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    print("Đã cấu hình Gemini với model 'gemini-2.5-flash' thành công!")
except Exception as e:
    print(f"Lỗi khi cấu hình Gemini: {e}")
    model = None

# --- Bước 4: Khởi tạo ứng dụng Flask ---
app = Flask(__name__)

# --- CÁC HÀM XỬ LÝ CHO FACEBOOK ---
def send_facebook_message(recipient_id, message_text):
    """Hàm gửi tin nhắn văn bản đến người dùng Facebook."""
    print(f"FACEBOOK: Đang gửi tin nhắn tới {recipient_id}")
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"
    }
    r = requests.post("https://graph.facebook.com/v19.0/me/messages", params=params, headers=headers, json=data)
    if r.status_code != 200:
        print(f"FACEBOOK: Lỗi khi gửi tin nhắn: {r.status_code} {r.text}")

@app.route('/', methods=['GET', 'POST'])
def facebook_webhook():
    """Webhook chỉ dành riêng cho Facebook."""
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        if token_sent == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return 'Invalid verification token', 403
    if request.method == 'POST':
        data = request.get_json()
        if data.get("object") == "page":
            for entry in data.get("entry", []):
                for messaging_event in entry.get("messaging", []):
                    if messaging_event.get("message"):
                        sender_id = messaging_event["sender"]["id"]
                        message_text = messaging_event["message"].get("text")
                        if message_text:
                            gemini_answer = get_gemini_response(message_text)
                            send_facebook_message(sender_id, gemini_answer)
        return "ok", 200

# --- CÁC HÀM XỬ LÝ CHO ZALO ---
def send_zalo_message(recipient_id, message_text):
    """Hàm gửi tin nhắn văn bản đến người dùng Zalo."""
    print(f"ZALO: Đang gửi tin nhắn tới {recipient_id}")
    headers = {
        'Content-Type': 'application/json',
        'access_token': ZALO_ACCESS_TOKEN
    }
    data = {
        "recipient": {"user_id": recipient_id},
        "message": {"text": message_text}
    }
    r = requests.post("https://openapi.zalo.me/v3.0/oa/message/cs", headers=headers, json=data)
    if r.status_code != 200:
        print(f"ZALO: Lỗi khi gửi tin nhắn: {r.json()}")

# --- PHẦN ĐÃ SỬA: ZALO WEBHOOK (Logic mới) ---
@app.route('/zalo', methods=['POST'])
def zalo_webhook():
    """Webhook chỉ dành riêng cho Zalo, với logic xử lý mạnh mẽ hơn."""
    data = request.get_json()
    
    # In ra để debug, bạn có thể xem trong Log của Render
    print(f"ZALO: Nhận được webhook: {data}")

    # Chỉ xử lý nếu đây là sự kiện người dùng gửi tin nhắn văn bản
    if data and data.get("event_name") == "user_send_text":
        sender_id = data["sender"]["id"]
        message_text = data["message"]["text"]
        
        # Lấy câu trả lời từ Gemini
        gemini_answer = get_gemini_response(message_text)
        # Gửi lại cho người dùng Zalo
        send_zalo_message(sender_id, gemini_answer)
        
    # Đối với MỌI yêu cầu khác (bao gồm cả yêu cầu "Kiểm tra" hoặc các sự kiện không xác định),
    # chúng ta sẽ trả về "ok" ngay lập tức để xác nhận với Zalo là đã nhận được.
    # Đây là chìa khóa để vượt qua bước xác minh.
    return "ok", 200

# --- HÀM XỬ LÝ TRUNG TÂM ---
def get_gemini_response(prompt):
    """Hàm này gửi yêu cầu đến Gemini và nhận lại câu trả lời."""
    if not model:
        return "Lỗi: Mô hình Gemini chưa được cấu hình."
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"GEMINI: Lỗi khi gọi API: {e}")
        return "Xin lỗi, tôi đang gặp một chút sự cố. Vui lòng thử lại sau."

# --- PHẦN XÁC THỰC DOMAIN CHO ZALO ---
@app.route('/<path:filename>')
def serve_static_file(filename):
    print(f"ZALO VERIFY: Yêu cầu file: {filename}")
    return send_from_directory('static', filename)

# --- CHẠY SERVER ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
