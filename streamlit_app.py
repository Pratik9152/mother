import streamlit as st
import requests
import json
import time
from streamlit_lottie import st_lottie

st.set_page_config(page_title="Payroll Assistant", layout="centered")

# ---------- Load Animation ----------
@st.cache_data
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_ai = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_qp1q7mct.json")

# ---------- UI Styling ----------
st.markdown("""
    <style>
        body {
            background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
            color: white;
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
            background-color: #00c6ff;
            color: black;
            text-align: right;
            float: right;
            clear: both;
        }
        .bot-msg {
            background-color: #1f2937;
            color: white;
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

# ---------- Header ----------
col1, col2 = st.columns([1, 5])
with col1:
    if lottie_ai:
        st_lottie(lottie_ai, height=80)
with col2:
    st.title("🤖 Payroll Assistant")
    st.caption("Smart answers based on your company policy")

# ---------- Admin Panel ----------
with st.sidebar:
    st.header("🔐 Admin Panel")
    pwd = st.text_input("Enter Admin Password", type="password")
    if "admin" not in st.session_state:
        st.session_state.admin = False
    if pwd == st.secrets["ADMIN_PASSWORD"]:
        st.session_state.admin = True
        st.success("Access Granted ✅")

# ---------- Policy ----------
if "policy" not in st.session_state:
    st.session_state.policy = st.secrets["DEFAULT_POLICY"]

if st.session_state.admin:
    st.sidebar.text_area("📝 Company Policy", value=st.session_state.policy, height=250, key="policy_editor")
    st.session_state.policy = st.session_state.policy_editor

# ---------- Chat UI ----------
st.markdown("### 💬 Ask your payroll question")
question = st.text_input("You:", key="user_input")

# ---------- OpenRouter Call ----------
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

# ---------- Show Response ----------
if question:
    st.markdown(f'<div class="chat-bubble user-msg">{question}</div>', unsafe_allow_html=True)
    st.markdown('<div class="chat-bubble bot-msg"><div class="typing"></div></div>', unsafe_allow_html=True)
    time.sleep(1.5)
    response = get_openrouter_reply(question, st.session_state.policy)
    st.markdown(f'<div class="chat-bubble bot-msg">{response}</div>', unsafe_allow_html=True)
