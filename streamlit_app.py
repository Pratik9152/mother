import streamlit as st
import requests
import json
import time
from streamlit_lottie import st_lottie

# ✅ Page settings (mobile-friendly)
st.set_page_config(page_title="Payroll Assistant", layout="centered")

# ✅ Stylish animated background + smooth chat styles
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
  background: linear-gradient(135deg, #1e3c72, #2a5298);
  background-size: 200% 200%;
  animation: gradient 12s ease infinite;
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

# ✅ Load Lottie animation
@st.cache_data
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_icon = load_lottieurl("https://assets7.lottiefiles.com/packages/lf20_cwqf3z6q.json")

# ✅ Welcome screen
if lottie_icon:
    st_lottie(lottie_icon, height=120)
st.markdown("### 🤖 Welcome to **Payroll Assistant**")
st.caption("⚡️ I can answer your payroll-related questions smartly as per your company's policy. Kindly begin typing below.")

# ✅ Admin Panel
with st.sidebar:
    st.header("🔐 Admin Panel")
    pwd = st.text_input("Admin Password", type="password")
    if "admin" not in st.session_state:
        st.session_state.admin = False
    if pwd == st.secrets["ADMIN_PASSWORD"]:
        st.session_state.admin = True
        st.success("✅ Access Granted")

# ✅ Policy
if "policy" not in st.session_state:
    st.session_state.policy = st.secrets["DEFAULT_POLICY"]

if st.session_state.admin:
    st.sidebar.text_area("✍️ Edit Payroll Policy", value=st.session_state.policy, height=300, key="policy_editor")
    st.session_state.policy = st.session_state.policy_editor

# ✅ Chat memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ✅ Chat box
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for sender, msg in st.session_state.chat_history:
        role_class = "user-msg" if sender == "user" else "bot-msg"
        st.markdown(f'<div class="chat-bubble {role_class}">{msg}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ✅ Chat input + button
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input("Ask your payroll query", label_visibility="collapsed", key="user_input")
with col2:
    send = st.button("Send")

# ✅ OpenRouter API call
def get_reply_from_openrouter(q, context):
    headers = {
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {"role": "system", "content": f"You are a payroll assistant. Use this company policy:\n\n{context}"},
            {"role": "user", "content": q}
        ]
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
        return res.json()["choices"][0]["message"]["content"]
    except:
        return "⚠️ Unable to fetch reply. Please check network/API key."

# ✅ On send
if send and user_input.strip():
    st.session_state.chat_history.append(("user", user_input))
    with chat_container:
        st.markdown(f'<div class="chat-bubble user-msg">{user_input}</div>', unsafe_allow_html=True)
        st.markdown('<div class="chat-bubble bot-msg"><div class="typing"></div></div>', unsafe_allow_html=True)
    time.sleep(1.2)
    reply = get_reply_from_openrouter(user_input, st.session_state.policy)
    st.session_state.chat_history.append(("bot", reply))
    st.rerun()
