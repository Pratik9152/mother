import streamlit as st
import requests
import json
import time
from streamlit_lottie import st_lottie

# ✅ Page configuration
st.set_page_config(page_title="Smart Payroll Assistant", layout="centered")

# ✅ Animated gradient background & chat styles
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
  background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #6a11cb, #2575fc);
  background-size: 400% 400%;
  animation: gradient 18s ease infinite;
  font-family: 'Segoe UI', sans-serif;
  padding-bottom: 100px;
}
@keyframes gradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
.chat-box {
    background-color: rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 15px;
    height: 450px;
    overflow-y: auto;
    margin-bottom: 12px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
}
.chat-bubble {
    padding: 10px 16px;
    border-radius: 12px;
    margin: 6px 0;
    max-width: 85%;
    font-size: 15px;
    animation: fadeIn 0.25s ease-in-out;
}
.user-msg {
    background-color: #4facfe;
    color: white;
    margin-left: auto;
}
.bot-msg {
    background-color: #1f1f1f;
    color: white;
    margin-right: auto;
}
.typing {
    width: 40px;
    height: 16px;
    display: inline-block;
    background: url('https://i.ibb.co/Fz1F2vR/typing-loader.gif') no-repeat center;
    background-size: contain;
}
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(5px);}
    to {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# ✅ Lottie animation loader
@st.cache_data
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

animation = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_cg3ukhgv.json")

# ✅ Welcome Header
if animation:
    st_lottie(animation, height=100)
st.markdown("## 🤖 Smart Payroll Chatbot")
st.caption("✨ Ask anything related to your payroll. The bot will answer only as per company policy provided by Admin.")

# ✅ Admin Panel
with st.sidebar:
    st.header("🔐 Admin Panel")
    pwd = st.text_input("Password", type="password")
    if "admin" not in st.session_state:
        st.session_state.admin = False
    if pwd == st.secrets["ADMIN_PASSWORD"]:
        st.session_state.admin = True
        st.success("✅ Access Granted")

# ✅ Default policy storage
if "policy" not in st.session_state:
    st.session_state.policy = st.secrets["DEFAULT_POLICY"]

if st.session_state.admin:
    st.sidebar.text_area("📝 Enter/Update Policy", value=st.session_state.policy, height=300, key="policy_editor")
    st.session_state.policy = st.session_state.policy_editor

# ✅ Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ✅ Chat Display
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for sender, msg in st.session_state.chat_history:
        role = "user-msg" if sender == "user" else "bot-msg"
        st.markdown(f'<div class="chat-bubble {role}">{msg}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ✅ Chat Input
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input("Type your payroll query here", label_visibility="collapsed", key="chat_input")
with col2:
    send = st.button("Send")

# ✅ OpenRouter API function
def get_reply_openrouter(query, policy_context):
    headers = {
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {"role": "system", "content": f"You are a payroll assistant. Use this exact company policy:\n\n{policy_context}"},
            {"role": "user", "content": query}
        ]
    }
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "⚠️ Network/API issue. Please check and try again."

# ✅ On Message Send
if send and user_input.strip():
    st.session_state.chat_history.append(("user", user_input))
    with chat_container:
        st.markdown(f'<div class="chat-bubble user-msg">{user_input}</div>', unsafe_allow_html=True)
        st.markdown('<div class="chat-bubble bot-msg"><div class="typing"></div></div>', unsafe_allow_html=True)
    time.sleep(1.2)
    answer = get_reply_openrouter(user_input, st.session_state.policy)
    st.session_state.chat_history.append(("bot", answer))
    st.rerun()
