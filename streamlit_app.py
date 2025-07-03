import streamlit as st
import requests
import json
from streamlit_lottie import st_lottie

# -------------------------- Page Config --------------------------
st.set_page_config(page_title="🤖 Ultra Payroll Assistant", layout="wide")

# -------------------------- Load Animation --------------------------
@st.cache_data
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_chat = load_lottieurl("https://lottie.host/91d05b2d-361f-4955-9df0-6b89cf4b3423/hEIfGyw96O.json")

# -------------------------- Header --------------------------
st.markdown("<style>body {background: linear-gradient(to right, #1f4037, #99f2c8); color: white;}</style>", unsafe_allow_html=True)

with st.container():
    left, right = st.columns([1, 3])
    with left:
        st_lottie(lottie_chat, height=120, key="chat")
    with right:
        st.title("💼 Payroll Assistant Chatbot")
        st.markdown("**Get instant payroll answers based on your company policy.**")

# -------------------------- Admin Login for Policy --------------------------
if "admin" not in st.session_state:
    st.session_state.admin = False

with st.sidebar:
    st.header("🔐 Admin Panel")
    password = st.text_input("Enter Admin Password", type="password")
    if password == st.secrets["ADMIN_PASSWORD"]:
        st.session_state.admin = True
        st.success("Admin Access Granted ✅")

# -------------------------- Policy Management --------------------------
if "policy" not in st.session_state:
    st.session_state.policy = st.secrets["DEFAULT_POLICY"]

if st.session_state.admin:
    st.sidebar.subheader("📝 Edit Policy")
    st.session_state.policy = st.sidebar.text_area("Paste your company payroll policy below:", value=st.session_state.policy, height=300)

# -------------------------- User Chat Interface --------------------------
st.markdown("### 💬 Chat Interface")
question = st.text_input("Ask a payroll-related question:")

# -------------------------- OpenRouter API Call --------------------------
def get_openrouter_reply(user_question, policy_context):
    headers = {
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {"role": "system", "content": f"You are a smart payroll chatbot. Only answer questions strictly based on this company policy:\n\n{policy_context}"},
            {"role": "user", "content": user_question}
        ]
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
        return res.json()["choices"][0]["message"]["content"]
    except:
        return "⚠️ Could not connect to OpenRouter API. Please check your key or internet connection."

# -------------------------- Show Chat Result --------------------------
if question:
    with st.spinner("🤖 Thinking..."):
        answer = get_openrouter_reply(question, st.session_state.policy)
        st.markdown("**🧠 Assistant:**")
        st.write(answer)
