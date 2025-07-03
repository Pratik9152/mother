import streamlit as st
import requests
import json
import time
from streamlit_lottie import st_lottie

st.set_page_config(page_title="Smart Payroll Assistant", layout="centered")

# 🌈 Animated background & stylish theme
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
  background: linear-gradient(-45deg, #ff6f91, #ff9671, #ffc75f, #f9f871);
  background-size: 500% 500%;
  animation: gradient 20s ease infinite;
  font-family: 'Segoe UI', sans-serif;
  padding-bottom: 100px;
}
@keyframes gradient {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
h2 {
    color: #fff700 !important;
    font-weight: bold;
    font-size: 30px !important;
    text-shadow: 2px 2px 5px #000;
}
span[data-baseweb="typography"] {
    color: white;
}
.chat-box {
    background-color: rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 15px;
    height: 450px;
    overflow-y: auto;
    margin-bottom: 12px;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255,255,255,0.15);
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
    background-color: #6a11cb;
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

# ✅ Load animated icon
@st.cache_data
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

animation = load_lottieurl("https://lottie.host/ea9aa876-9171-4f07-9107-9d6bc00daed0/luhueXvlaT.json")

if animation:
    st_lottie(animation, height=120)

st.markdown("## 🤖 Smart Payroll Chatbot")

# 🔐 Admin Panel
with st.sidebar:
    st.header("🔐 Admin Panel")
    pwd = st.text_input("Password", type="password")
    if "admin" not in st.session_state:
        st.session_state.admin = False
    if pwd == st.secrets["ADMIN_PASSWORD"]:
        st.session_state.admin = True
        st.success("✅ Access Granted")

# 📄 Policy input (admin-only)
if "policy" not in st.session_state:
    st.session_state.policy = st.secrets["DEFAULT_POLICY"]

if st.session_state.admin:
    st.sidebar.text_area("📝 Paste Your Payroll Policy", value=st.session_state.policy, height=300, key="policy_editor")
    st.session_state.policy = st.session_state.policy_editor

# 💬 Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 💬 Chat Box
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for sender, msg in st.session_state.chat_history:
        role = "user-msg" if sender == "user" else "bot-msg"
        st.markdown(f'<div class="chat-bubble {role}">{msg}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ✅ Chat input + button
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input("Type your payroll question...", label_visibility="collapsed", key="chat_input")
with col2:
    send = st.button("Send")

# 🔁 Smart Reply using OpenRouter
def get_reply_openrouter(query, policy_context):
    headers = {
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {"role": "system", "content": f"You are a smart Indian payroll assistant. Answer ONLY based on the given policy below. Do NOT reply with unrelated points. If policy is missing, say 'not mentioned'. Policy:\n{policy_context}"},
            {"role": "user", "content": query}
        ]
    }
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
        return r.json()["choices"][0]["message"]["content"]
    except:
        return "⚠️ Network/API error. Please verify API key or connection."

# 🚀 On Send
if send and user_input.strip():
    st.session_state.chat_history.append(("user", user_input))
    with chat_container:
        st.markdown(f'<div class="chat-bubble user-msg">{user_input}</div>', unsafe_allow_html=True)
        st.markdown('<div class="chat-bubble bot-msg"><div class="typing"></div></div>', unsafe_allow_html=True)
    time.sleep(1.2)
    answer = get_reply_openrouter(user_input, st.session_state.policy)
    st.session_state.chat_history.append(("bot", answer))
    st.rerun()
