# --- Bước 1: Nhập các thư viện cần thiết ---
import os
import json
from flask import Flask, request
import requests
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import firebase_admin
from firebase_admin import credentials, firestore

# --- Bước 2: Tải các biến môi trường ---
load_dotenv()
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
PAGE_TOKENS_JSON = os.getenv('PAGE_TOKENS_JSON')
FIREBASE_CREDENTIALS_JSON = os.getenv('FIREBASE_CREDENTIALS_JSON')

# Tải các tùy chọn cấu hình
HUMAN_TAKEOVER_ENABLED = os.getenv('HUMAN_TAKEOVER_ENABLED', 'false').lower() == 'true'
BOT_RESUME_MINUTES = int(os.getenv('BOT_RESUME_MINUTES', '30'))

# Tải và xử lý "chùm chìa khóa"
PAGE_TOKEN_MAP = json.loads(PAGE_TOKENS_JSON) if PAGE_TOKENS_JSON else {}

# --- PHẦN MỚI: Khởi tạo kết nối với "BỘ NÃO VĨNH VIỄN" FIRESTORE ---
try:
    # Kiểm tra xem biến môi trường có tồn tại không
    if FIREBASE_CREDENTIALS_JSON:
        cred_json = json.loads(FIREBASE_CREDENTIALS_JSON)
        cred = credentials.Certificate(cred_json)
        # Kiểm tra xem ứng dụng Firebase đã được khởi tạo chưa
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("✅ Kết nối với Firestore (bộ nhớ vĩnh viễn) thành công!")
    else:
        print("❌ Lỗi: Biến môi trường FIREBASE_CREDENTIALS_JSON không được thiết lập.")
        db = None
except Exception as e:
    print(f"❌ Lỗi khi kết nối Firestore: {e}")
    db = None

# --- "CUỐN SÁCH KIẾN THỨC" VÀ "BỘ QUY TẮC" CỦA BOT ---
KNOWLEDGE_BASE = """
# Thông tin chung
- Tên công ty: Xưởng sản xuất túi vải Quà Tặng Thành Công.
- Lĩnh vực: Sản xuất trực tiếp các loại túi vải theo yêu cầu cho khách hàng doanh nghiệp (B2B), không bán lẻ.
- Giờ làm việc: Thứ 2 - Thứ 7, từ 8:00 - 17:00.

# Sản phẩm và Dịch vụ
- Sản phẩm chính: Túi vải canvas, túi vải bố, túi vải không dệt, túi đay, túi linen, túi rút, và ba lô dây rút.
- Các loại vải: Vải bố, canvas, không dệt, đay, linen, vải dù (kháng nước và không kháng nước), calicot.
- Tùy chỉnh: Nhận in ấn logo, hình ảnh theo thiết kế của khách hàng.
- Phương pháp in: In lụa (giá rẻ, chất lượng khá), In chuyển nhiệt/PET (giá vừa phải, chất lượng cao), In decal (giá cao, độ sắc nét tốt nhất). Tùy chọn phương pháp in sẽ phụ thuộc vào loại vải.
- Dịch vụ miễn phí: Tư vấn và thiết kế mẫu, sản xuất 2 túi mẫu, giao hàng nội thành TP.HCM.

# Chính sách kinh doanh
- Số lượng đặt hàng tối thiểu (MOQ): 100 túi/đơn hàng. Riêng túi vải không dệt là 500 túi/đơn hàng.
- Lý do có MOQ: Để tối ưu hóa chi phí sản xuất và in ấn, mang lại giá thành tốt nhất cho khách hàng.
- Linh hoạt: MOQ có thể thương lượng tùy thuộc vào ngân sách của khách hàng. Nếu khách hàng chấp nhận giá thành cao hơn, xưởng có thể sản xuất số lượng ít hơn.

# Thông tin báo giá
- Khoảng giá tham khảo: Từ 10.000đ đến 80.000đ mỗi túi.
- Các yếu tố ảnh hưởng đến giá: Số lượng (càng nhiều giá càng rẻ), chất liệu vải, kích thước, số màu in, độ phức tạp thiết kế, phương pháp in, và thời gian sản xuất.

# Thông tin liên hệ
- Văn phòng: 154 Phạm Văn Chiêu, P. Thông Tây Hội, TP.HCM.
- Xưởng may: Xã Đông Thạnh, TP.HCM.
- Điện thoại: 02837112666
- Zalo tư vấn: 0835130333
- Email: quatangthanhcong@gmail.com
"""

# --- "BỘ QUY TẮC" CHO BOT (SYSTEM INSTRUCTIONS) ---
SYSTEM_INSTRUCTION = f"""
# VAI TRÒ VÀ MỤC TIÊU
- **Tên của bạn là Minh Châu.** Bạn là một tư vấn viên chuyên nghiệp, KHÔNG phải là AI hay bot.
- **Bạn làm việc cho "Xưởng may túi vải Thành Công"**, KHÔNG phải "Shop".
- **Mục tiêu chính:** Sàng lọc khách hàng doanh nghiệp (B2B) tiềm năng, thu thập thông tin nhu cầu ban đầu và lấy thông tin liên hệ (SĐT/Zalo) để đội ngũ kinh doanh tư vấn chi tiết.

# QUY TRÌNH TƯ VẤN BẮT BUỘC
Bạn phải tuân thủ nghiêm ngặt quy trình từng bước sau, với phong cách giao tiếp tự nhiên như con người:
1.  **Chào hỏi:** Chào khách hàng (nếu biết tên, hãy dùng tên của họ), giới thiệu bạn là Minh Châu từ Xưởng may Thành Công và hỏi về loại túi họ đang quan tâm. Không nhắc lại lời giới thiệu ở mỗi câu trả lời và luôn xưng mình là "Em", gọi khách là Anh/chị nếu chưa biết giới tính.
2.  **Hỏi Số Lượng & MOQ:** Hỏi khách cần may bao nhiêu túi. Nhẹ nhàng đề cập chính sách số lượng tối thiểu (100 túi cho hầu hết các loại, 500 túi cho vải không dệt).
3.  **Hỏi Ngân Sách:** Khéo léo hỏi về ngân sách dự kiến của khách hàng. Đây là thông tin quan trọng nhất để tư vấn.
4.  **Xử lý MOQ:**
    - Nếu khách hỏi **dưới mức tối thiểu**, không từ chối ngay. Lịch sự giải thích rằng MOQ là để tối ưu chi phí nhưng xưởng rất linh hoạt tùy theo ngân sách. Khuyến khích khách cung cấp thông tin liên hệ để đội kinh doanh tư vấn giải pháp tốt nhất.
    - Nếu khách hỏi **từ 100 túi trở lên**, tiếp tục các bước sau.
5.  **Thu thập thông tin thêm:** Hỏi tuần tự từng câu hỏi ngắn gọn về: loại vải, tình trạng thiết kế (đã có sẵn hay cần hỗ trợ), và thời gian mong muốn nhận hàng.
6.  **Lấy và Xác nhận Thông Tin Liên Hệ:**
    - Trước khi kết thúc, đề nghị khách hàng cung cấp SĐT hoặc Zalo cá nhân để đội kinh doanh tiện liên hệ.
    - Sau khi khách cung cấp, **bắt buộc phải hỏi lại để xác nhận số đã chính xác chưa.**
    - Khi khách đã xác nhận, hãy cảm ơn và thông báo rằng đội kinh doanh sẽ liên hệ lại.

# PHONG CÁCH GIAO TIẾP VÀ KỸ NĂNG
- **Tự nhiên như người thật:** Sử dụng ngôn ngữ đời thường, thân thiện, tránh văn phong máy móc.
- **Tư duy tối giản:** Giao tiếp ngắn gọn, rõ ràng, mỗi lần chỉ hỏi một thông tin. Không lặp lại lời chào/giới thiệu không cần thiết.
- **Hiểu ngôn ngữ khách hàng:** Nhận diện và hiểu các từ viết tắt, teencode của khách hàng để trả lời đúng trọng tâm.
- **Linh hoạt theo ngân sách:** Luôn ưu tiên và bám sát vào ngân sách khách hàng cung cấp. MOQ có thể thương lượng nếu khách chấp nhận giá thành cao hơn.
- **Ghi nhớ thông tin:** Luôn ghi nhớ các thông tin khách đã cung cấp trong suốt cuộc trò chuyện để tránh hỏi lại.

# CÁC QUY TẮC XỬ LÝ ĐẶC BIỆT
- **Bám sát kiến thức:** Chỉ được phép sử dụng thông tin trong phần "KIẾN THỨC CUNG CẤP" dưới đây. Tuyệt đối không tự bịa ra thông tin hoặc dùng kiến thức bên ngoài.
- **Xử lý tin nhắn tuyển dụng:** Nếu khách gửi các từ khóa như "Mô tả công việc", "Yêu cầu công việc", "Phúc lợi", "Nộp hồ sơ", **KHÔNG trả lời bất cứ điều gì.**
- **Thông tin người tạo:** Nếu được hỏi, người tạo ra bạn là anh "Tony An Lạc".

# KIẾN THỨC CUNG CẤP
---
{KNOWLEDGE_BASE}
---
"""

# --- Bước 3: Cấu hình mô hình Gemini ---
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        system_instruction=SYSTEM_INSTRUCTION
    )
    print("Đã cấu hình Gemini với BỘ QUY TẮC thành công!")
except Exception as e:
    print(f"Lỗi khi cấu hình Gemini: {e}")
    model = None

# --- Bước 4: Khởi tạo ứng dụng Flask ---
app = Flask(__name__)

# --- HÀM LẤY THÔNG TIN NGƯỜI DÙNG TỪ FACEBOOK ---
def get_user_profile(sender_id, page_access_token):
    try:
        r = requests.get(f"https://graph.facebook.com/v19.0/{sender_id}", params={"fields": "first_name,last_name", "access_token": page_access_token})
        if r.status_code == 200:
            user_profile = r.json()
            return f"{user_profile.get('first_name', '')} {user_profile.get('last_name', '')}".strip()
    except Exception as e:
        print(f"Lỗi khi lấy thông tin người dùng: {e}")
    return None

# --- Bước 5: Hàm gửi tin nhắn Facebook ---
def send_message(recipient_id, message_text, page_access_token):
    params = {"access_token": page_access_token}
    headers = {"Content-Type": "application/json"}
    data = {"recipient": {"id": recipient_id}, "message": {"text": message_text}, "messaging_type": "RESPONSE"}
    requests.post("https://graph.facebook.com/v19.0/me/messages", params=params, headers=headers, json=data)

# --- Bước 6: HÀM GỌI GEMINI (ĐÃ SỬA LỖI FIRESTORE) ---
def get_gemini_response(sender_id, prompt):
    if not model or not db:
        return "Lỗi hệ thống: Bot chưa sẵn sàng."

    doc_ref = db.collection('chat_sessions').document(sender_id)
    doc = doc_ref.get()
    history = doc.to_dict().get('history', []) if doc.exists else []
    
    chat = model.start_chat(history=history)
    
    try:
        response = chat.send_message(prompt)
        
        # SỬA LỖI: Chuyển đổi đối tượng history phức tạp thành định dạng đơn giản
        # trước khi lưu vào Firestore để tránh lỗi 'Cannot convert to a Firestore Value'.
        serializable_history = [
            {'role': msg.role, 'parts': [part.text for part in msg.parts]}
            for msg in chat.history
        ]
        
        # Cập nhật lịch sử đã được "dịch" lên Firestore
        doc_ref.set({'history': serializable_history}, merge=True)
        
        return response.text
    except Exception as e:
        print(f"Lỗi khi gọi API Gemini: {e}")
        return "Xin lỗi, tôi đang gặp một chút sự cố."

# --- Bước 7: Webhook Endpoint (sử dụng Firestore) ---
@app.route('/', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        if token_sent == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return 'Invalid verification token', 403
    
    if request.method == 'POST':
        data = request.get_json()
        if data.get("object") == "page":
            for entry in data.get("entry", []):
                page_id = entry.get("id")
                page_access_token = PAGE_TOKEN_MAP.get(page_id)
                if not page_access_token: continue

                for messaging_event in entry.get("messaging", []):
                    # Xử lý tin nhắn do NHÂN VIÊN gửi
                    if messaging_event.get("message", {}).get("is_echo") and HUMAN_TAKEOVER_ENABLED:
                        sender_id = messaging_event["recipient"]["id"]
                        if db:
                            doc_ref = db.collection('chat_sessions').document(sender_id)
                            doc_ref.set({'control': 'HUMAN', 'last_human_timestamp': firestore.SERVER_TIMESTAMP}, merge=True)
                        continue

                    # Xử lý tin nhắn do KHÁCH HÀNG gửi
                    if messaging_event.get("message") and not messaging_event.get("message", {}).get("is_echo"):
                        sender_id = messaging_event["sender"]["id"]
                        message_text = messaging_event["message"].get("text")

                        if not db:
                            send_message(sender_id, "Lỗi hệ thống: Không thể kết nối đến bộ nhớ.", page_access_token)
                            continue

                        doc_ref = db.collection('chat_sessions').document(sender_id)
                        doc = doc_ref.get()
                        current_state = doc.to_dict() if doc.exists else {}
                        
                        is_new_conversation = not doc.exists
                        if is_new_conversation:
                            user_name = get_user_profile(sender_id, page_access_token)
                            doc_ref.set({'user_name': user_name, 'control': 'BOT'})
                            current_state['user_name'] = user_name

                        should_bot_reply = True
                        if current_state.get('control') == 'HUMAN' and HUMAN_TAKEOVER_ENABLED:
                            should_bot_reply = False
                            if current_state.get('last_human_timestamp'):
                                time_since_human = datetime.now(timezone.utc) - current_state['last_human_timestamp'].replace(tzinfo=timezone.utc)
                                if time_since_human > timedelta(minutes=BOT_RESUME_MINUTES):
                                    doc_ref.set({'control': 'BOT'}, merge=True)
                                    should_bot_reply = True

                        if message_text and should_bot_reply:
                            prompt_to_send = message_text
                            if is_new_conversation and current_state.get('user_name'):
                                prompt_to_send = f"(Tên khách hàng là {current_state['user_name']}) {message_text}"
                            
                            gemini_answer = get_gemini_response(sender_id, prompt_to_send)
                            send_message(sender_id, gemini_answer, page_access_token)
        return "ok", 200

# --- Bước 8: Chạy server (Đã được Gunicorn quản lý) ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
