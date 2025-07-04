import streamlit as st 
import requests 
import json 
from streamlit_lottie import st_lottie
from datetime import datetime

---------- PAGE CONFIGURATION ----------

st.set_page_config(page_title="Smart Payroll Chatbot", layout="centered")

---------- CUSTOM STYLES ----------

st.markdown("""

<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #1e1e60, #283e51, #485563);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
    font-family: 'Segoe UI', sans-serif;
    padding: 2rem;
    color: white;
}
@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
.message {
    padding: 10px 15px;
    border-radius: 15px;
    margin-bottom: 10px;
    max-width: 85%;
    display: inline-block;
    position: relative;
    word-wrap: break-word;
    font-size: 16px;
}
.bot-bubble {
    background-color: #f0f0f0;
    color: #000;
    align-self: flex-start;
    border-bottom-left-radius: 0;
    margin-right: auto;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
}
.user-bubble {
    background-color: #007bff;
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 0;
    margin-left: auto;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
}
.input-container {
    position: fixed;
    bottom: 2rem;
    left: 2rem;
    right: 2rem;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 10px;
    backdrop-filter: blur(5px);
    z-index: 999;
}
button[kind="primary"] {
    background-color: #00c9ff !important;
    color: black !important;
    font-weight: bold;
}
</style>""", unsafe_allow_html=True)

---------- LOAD LOTTIE ANIMATION ----------

def load_lottie_url(url): r = requests.get(url) if r.status_code != 200: return None return r.json()

lottie_bot = load_lottie_url("https://lottie.host/f06a7f33-dff7-4d5a-a3b3-29cb765cd3f5/VHYJ6Ykr8G.json") if lottie_bot: st_lottie(lottie_bot, height=150, key="bot")

st.markdown("## 🤖 <span style='color:white;'>Smart Payroll Chatbot</span>", unsafe_allow_html=True) st.markdown("<p style='color:white;'>Ask anything related to Indian payroll: PF, LTA, gratuity, F&F, bonus, salary.</p>", unsafe_allow_html=True)

---------- ADMIN PANEL ----------

with st.sidebar: st.subheader("🔐 Admin Login") password = st.text_input("Enter Admin Password", type="password") if password == st.secrets["ADMIN_PASSWORD"]: st.success("✅ Access Granted") policy_text = st.text_area("📝 Paste Additional Payroll Policy", height=300) if policy_text: st.session_state["policy_data"] = policy_text else: st.warning("Admin login required to edit policy.")

---------- CHAT HISTORY STATE ----------

if "chat_history" not in st.session_state: st.session_state.chat_history = []

---------- DISPLAY CHAT HISTORY ----------

for sender, msg in st.session_state.chat_history: role_class = "user-bubble" if sender == "user" else "bot-bubble" st.markdown(f"<div class='message {role_class}'><b>{'You' if sender=='user' else 'Bot'}:</b><br>{msg}</div>", unsafe_allow_html=True)

---------- CHAT INPUT & RESPONSE ----------

st.markdown("<div class='input-container'>", unsafe_allow_html=True) user_input = st.text_input("Ask payroll question...", key="chatbox_fixed") if st.button("Send", key="send_fixed") and user_input: st.session_state.chat_history.append(("user", user_input))

# Combine default and admin policy
combined_policy = f"{st.secrets.get('DEFAULT_POLICY', '')}\n{st.session_state.get('policy_data', '')}"
headers = {
    "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
    "Content-Type": "application/json"
}
payload = {
    "model": "mistralai/mixtral-8x7b-instruct",
    "messages": [
        {"role": "system", "content": "You are a smart payroll assistant. Only answer Indian payroll-related queries. Be short, helpful, and say 'Not mentioned' if unsure."},
        {"role": "user", "content": f"Policy:\n{combined_policy}\n\nQuestion: {user_input}"}
    ]
}

try:
    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
    reply = res.json()["choices"][0]["message"]["content"]
except:
    reply = "⚠️ Could not respond."

st.session_state.chat_history.append(("bot", reply))

st.markdown("</div>", unsafe_allow_html=True)

