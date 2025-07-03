import streamlit as st
import requests
import json
import time
from streamlit_lottie import st_lottie

# ✅ Page config
st.set_page_config(page_title="Payroll Assistant", layout="wide")

# ✅ Gradient animated background
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
  background: linear-gradient(-45deg, #1f4037, #99f2c8, #6a11cb, #2575fc);
  background-size: 400% 400%;
  animation: gradient 15s ease infinite;
}
@keyframes gradient {
  0% {background-position: 0% 50%;}
  50% {background-position: 100% 50%;}
  100% {background-position: 0% 50%;}
}
*::-webkit-scrollbar {
  width: 8px;
}
*::-webkit-scrollbar-thumb {
  background-color: #444;
  border-radius: 10px;
}
.chat-box {
    background-color: rgba(255,255,255,0.06);
    border-radius: 15px;
    padding: 20px;
    height: 500px;
    overflow-y: auto;
    margin-bottom: 10px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
}
.chat-bubble {
    padding: 12px 20px;
    border-radius: 15px;
    margin: 10px 0;
    max-width: 80%;
    display: inline-block;
    animation: fadeIn 0.3s ease-in-out;
}
.user-msg {
    background: linear-gradient(145deg, #00c6ff, #0072ff);
    color: #fff;
    align-self: flex-end;
    float: right;
    clear: both;
}
.bot-msg {
    background-color: #1f1f1f;
    color: #fff;
    float: left;
    clear: both;
}
.typing {
    width: 50px;
    height: 20px;
    display: inline-block;
    background: url('https://i.ibb.co/Fz1F2vR/typing-loader.gif') no-repeat center;
    background-size: contain;
}
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}
</style>
""", unsafe_allow_html=True)

# ✅ Load Lottie animation
@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

lottie_ai = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_qp1q7mct.json")

# ✅ Header
col1, col2 = st.columns([1, 5])
with col1:
    if lottie_ai:
        st_lottie(lottie_ai, height=80)
with col2:
    st.title("💼 Payroll Assistant Chatbot")
    st.caption("Smart answers based on your company policy")

# ✅ Admin panel
with st.sidebar:
    st.header("🔐 Admin Panel")
    pwd = st.text_input("Enter Admin Password", type="password")
    if "admin" not in st.session_state:
        st.session_state.admin = False
    if pwd == st.secrets["ADMIN_PASSWORD"]:
        st.session_state.admin = True
        st.success("Access Granted ✅")

# ✅ Policy load/save
if "policy" not in st.session_state:
    st.session_state.policy = st.secrets["DEFAULT_POLICY"]

if st.session_state.admin:
    st.sidebar.text_area("📝 Company Policy", value=st.session_state.policy, height=250, key="policy_editor")
    st.session_state.policy = st.session_state.policy_editor

# ✅ Chat memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ✅ Chat UI box
st.markdown("### 💬 Ask your payroll question")
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    for sender, msg in st.session_state.chat_history:
        bubble_class = "user-msg" if sender == "user" else "bot-msg"
        st.markdown(f'<div class="chat-bubble {bubble_class}">{msg}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ✅ Input + send button pinned at bottom
col_input, col_button = st.columns([5, 1])
with col_input:
    user_input = st.text_input("Type your message", label_visibility="collapsed", key="chat_input")
with col_button:
    send = st.button("Send")

# ✅ OpenRouter call
def get_openrouter_reply(q, context):
    headers = {
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {"role": "system", "content": f"Answer ONLY based on this company policy:\n\n{context}"},
            {"role": "user", "content": q}
        ]
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
        return res.json()["choices"][0]["message"]["content"]
    except:
        return "⚠️ Unable to fetch reply. Check your key or network."

# ✅ On send
if send and user_input.strip():
    st.session_state.chat_history.append(("user", user_input))
    with chat_container:
        st.markdown(f'<div class="chat-bubble user-msg">{user_input}</div>', unsafe_allow_html=True)
        st.markdown('<div class="chat-bubble bot-msg"><div class="typing"></div></div>', unsafe_allow_html=True)
    time.sleep(1.5)
    reply = get_openrouter_reply(user_input, st.session_state.policy)
    st.session_state.chat_history.append(("bot", reply))
    st.rerun()
