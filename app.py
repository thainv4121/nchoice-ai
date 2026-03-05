import streamlit as st
from groq import Groq
import time

st.set_page_config(page_title="NChoice AI", page_icon="💬", layout="centered")

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {display: none;}
    [data-testid="stDecoration"] {display: none;}

    /* Chữ tiêu đề nhỏ gọn */
    .stApp h3, .stApp h4 {
        font-size: 1rem !important;
        font-weight: 600 !important;
        margin-bottom: 4px !important;
    }

    /* Chữ trong tin nhắn */
    [data-testid="stChatMessageContent"] p {
        font-size: 13px !important;
        line-height: 1.6 !important;
    }

    /* Input placeholder rõ hơn */
    [data-testid="stChatInput"] textarea::placeholder {
        font-size: 13px !important;
        opacity: 0.6 !important;
    }

    /* Nút gửi màu xanh */
    [data-testid="stChatInput"] button {
        background-color: #2563eb !important;
        border-radius: 8px !important;
    }

    /* Disclaimer nhỏ gọn */
    .contact-box {
        background: rgba(37,99,235,0.15) !important;
        border: 1px solid rgba(37,99,235,0.3) !important;
        border-radius: 10px;
        padding: 10px 12px;
        margin-top: 6px;
        font-size: 12px;
    }
    .contact-box p {
        margin: 0 0 8px 0 !important;
        font-weight: 600 !important;
        font-size: 12px !important;
    }
    .contact-btn {
        display: inline-block;
        background: #2563eb;
        color: white !important;
        padding: 6px 14px;
        border-radius: 8px;
        text-decoration: none !important;
        font-size: 12px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ---- URL trang liên hệ----
CONTACT_URL = "https://zalo.me/g/hsuyjk983"

CONTACT_HTML = f"""
<div class="contact-box">
    <p>💬 Tham gia cộng đồng để tìm hiểu thêm nhiều điều thú vị nhé!</p>
    <a href="{CONTACT_URL}" target="_blank" class="contact-btn"> Tham gia ngay</a>
</div>
"""

st.markdown("""
<div style="background:rgba(234,179,8,0.15); border:1px solid rgba(234,179,8,0.4); 
border-radius:8px; padding:6px 10px; font-size:13px; 
color:#fcd34d; line-height:1.4;">
⚠️ LƯU Ý: Các thông tin được cung cấp bởi AI mang tính tham khảo. Vui lòng kiểm tra lại và cẩn trọng khi đưa ra quyết định đầu tư.
</div>
""", unsafe_allow_html=True)

st.write("#### Xin chào! Tôi có thể giúp gì cho bạn về thị trường vàng?")

SYSTEM_PROMPT = """Bạn là AI được xây dựng bởi Nguyễn Thị Bích Ngọc, còn gọi là Ngọc Choice, hay NChoice.
Hỗ trợ người dùng về: kiến thức tài chính, thị trường vàng Việt Nam và quốc tế, phân tích cũng như đánh giá tình hình chung, đưa ra dự báo xu hướng thị trường, cập nhật các thông tin mới nhất liên quan.
Trước khi trả lời về giá vàng, xu hướng thị trường, hoặc tình hình kinh tế, hãy luôn tìm kiếm thông tin mới nhất trên internet để đưa ra nhận định chính xác.
Đưa ra quan điểm rõ ràng dựa trên dữ liệu thực tế, không mơ hồ.
Trả lời bằng tiếng Việt, ngắn gọn, rõ ràng, theo từng bước đánh số nếu cần.
Chỉ trả lời câu hỏi về nội dung liên quan đến nội dung được phép hỗ trợ, với những câu hỏi không thuộc lĩnh vực của bạn hãy từ chối do không phải là chức năng.
Cuối mỗi câu trả lời, xuống dòng, thêm dòng in nghiêng: '\n_Lưu ý: Kiểm tra lại thông tin và cẩn trọng trước khi đưa ra quyết định._"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # Hiển thị nút liên hệ sau mỗi câu trả lời của bot
        if msg["role"] == "assistant":
            st.markdown(CONTACT_HTML, unsafe_allow_html=True)

if prompt := st.chat_input("Nhập câu hỏi của bạn ở đây nhé"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    import time

with st.chat_message("assistant"):
    with st.spinner("Đang xử lý..."):
        
        # Thử compound-beta trước, nếu lỗi fallback sang llama-4
        max_retries = 3
        answer = None
        
        for attempt in range(max_retries):
            try:
                response = client.chat.completions.create(
                    model="compound-beta",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        *[{"role": m["role"], "content": m["content"]}
                          for m in st.session_state.messages]
                    ],
                    max_tokens=1024
                )
                answer = response.choices[0].message.content
                break  # Thành công thì thoát vòng lặp

            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)  # Chờ 2 giây rồi thử lại
                else:
                    # Sau 3 lần thất bại, dùng model dự phòng
                    try:
                        response = client.chat.completions.create(
                            model="meta-llama/llama-4-scout-17b-16e-instruct",
                            messages=[
                                {"role": "system", "content": SYSTEM_PROMPT},
                                *[{"role": m["role"], "content": m["content"]}
                                  for m in st.session_state.messages]
                            ],
                            max_tokens=1024
                        )
                        answer = response.choices[0].message.content
                    except Exception:
                        answer = "⚠️ Hệ thống đang bận, vui lòng thử lại sau ít phút."

        st.markdown(answer)
        st.markdown(CONTACT_HTML, unsafe_allow_html=True)

st.session_state.messages.append({"role": "assistant", "content": answer})
