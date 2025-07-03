import streamlit as st
import requests
import json
from streamlit_lottie import st_lottie

# Set app config
st.set_page_config(page_title="Smart Payroll Assistant", layout="centered")

# 🌈 Animated background + chatbot header
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #f857a6, #ff5858, #ffc371, #00c9ff);
    background-size: 500% 500%;
    animation: gradient 12s ease infinite;
    font-family: 'Segoe UI', sans-serif;
}
@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
h1 {
    color: #fff;
    text-align: center;
    font-size: 38px;
    text-shadow: 2px 2px 5px #000;
}
</style>
""", unsafe_allow_html=True)

def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_bot = load_lottie_url("https://lottie.host/f06a7f33-dff7-4d5a-a3b3-29cb765cd3f5/VHYJ6Ykr8G.json")
if lottie_bot:
    st_lottie(lottie_bot, height=150, key="bot")

st.markdown("## 🤖 <span style='color:white;'>Smart Payroll Chatbot</span>", unsafe_allow_html=True)
st.markdown("<p style='color:white; text-align:center;'>Ask anything about salary, PF, leave, F&F, bonus, and more!</p>", unsafe_allow_html=True)

# 🔐 Admin panel for uploading policy
with st.sidebar:
    st.subheader("🔐 Admin Login")
    password = st.text_input("Enter Admin Password", type="password")
    if password == st.secrets["ADMIN_PASSWORD"]:
        st.success("✅ Access Granted")
        policy_text = st.text_area("📝 Enter or Paste Payroll Policy", height=300)
        if policy_text:
            st.session_state["policy_data"] = policy_text
    else:
        st.warning("Admin login required to update policy.")

# 💬 Chat interaction
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

query = st.text_input("💬 Type your question here...")

if st.button("Send") and query:
    st.session_state.chat_history.append(("user", query))

    policy = st.session_state.get("policy_data", "")
    headers = {
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {
                "role": "system",
                "content": "You are a smart payroll assistant. Respond directly and clearly using the given policy. Avoid phrases like 'as per policy'. If info not found, say 'Not mentioned'."
            },
            {"role": "user", "content": f"Policy:\n{policy}\n\nQuestion: {query}"}
        ]
    }

    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
        reply = res.json()["choices"][0]["message"]["content"]
    except:
        reply = "⚠️ Unable to fetch reply. Check API or internet."

    st.session_state.chat_history.append(("bot", reply))

# 📜 Display full chat history
for sender, msg in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"<div style='background-color:#ffe6e6;padding:10px;border-radius:10px;margin-bottom:5px'><b>You:</b><br>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='background-color:#e6ffe6;padding:10px;border-radius:10px;margin-bottom:10px'><b>Bot:</b><br>{msg}</div>", unsafe_allow_html=True)
