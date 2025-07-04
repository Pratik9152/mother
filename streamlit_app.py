import streamlit as st import requests import json from streamlit_lottie import st_lottie from datetime import datetime

-------------- PAGE SETUP --------------

st.set_page_config(page_title="Smart Payroll Assistant", layout="centered")

-------------- STYLES --------------

st.markdown("""

<style>
@import url('https://fonts.googleapis.com/css2?family=Rubik:wght@400;600&display=swap');

[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e);
    background-size: 600% 600%;
    animation: gradient 20s ease infinite;
    font-family: 'Rubik', sans-serif;
    color: white;
}
@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
h1, h2, h4 {
    text-align: center;
    text-shadow: 2px 2px 4px #000;
}
.typing {
    width: 80px;
    height: 20px;
    background: rgba(255,255,255,0.4);
    border-radius: 50px;
    position: relative;
    animation: blink 1.5s infinite;
    margin: 10px auto;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}
.bubble {
    padding: 10px 15px;
    margin: 10px;
    max-width: 85%;
    border-radius: 18px;
    position: relative;
    box-shadow: 0px 0px 10px rgba(0,0,0,0.2);
}
.user-bubble {
    background-color: #e0ffe0;
    color: #000;
    margin-left: auto;
    border-bottom-right-radius: 0;
}
.bot-bubble {
    background-color: #d0d0ff;
    color: #000;
    margin-right: auto;
    border-bottom-left-radius: 0;
}
.send-button {
    background-color: #00c9ff;
    color: white;
    padding: 12px 30px;
    border: none;
    border-radius: 10px;
    font-weight: bold;
    font-size: 16px;
    cursor: pointer;
    transition: background-color 0.3s ease;
}
.send-button:hover {
    background-color: #0099cc;
}
</style>""", unsafe_allow_html=True)

-------------- HEADER + ANIMATION --------------

def load_lottie_url(url): r = requests.get(url) if r.status_code != 200: return None return r.json()

lottie_bot = load_lottie_url("https://lottie.host/f06a7f33-dff7-4d5a-a3b3-29cb765cd3f5/VHYJ6Ykr8G.json") if lottie_bot: st_lottie(lottie_bot, height=180, key="bot")

st.markdown("""

<h1>🤖 Smart Payroll Assistant</h1>
<h4>Ask me anything related to Indian payroll!</h4>
""", unsafe_allow_html=True)-------------- CHAT STORAGE --------------

if "chat_history" not in st.session_state: st.session_state.chat_history = []

-------------- ADMIN SIDEBAR (Optional) --------------

with st.sidebar: st.subheader("🔐 Admin Login") password = st.text_input("Enter Admin Password", type="password") if password == st.secrets["ADMIN_PASSWORD"]: st.success("✅ Access Granted") new_policy = st.text_area("📝 Add to Policy", height=250) if new_policy: st.session_state["custom_policy"] = new_policy else: st.info("Login to add company policy.")

-------------- CHAT INPUT + SEND --------------

st.markdown("<div class='typing'></div>", unsafe_allow_html=True) query = st.text_input("", placeholder="💬 Type your payroll question here...", key="chatbox")

if st.button("Send", key="send-btn", type="primary") and query: st.session_state.chat_history.append(("user", query))

# Combine default + custom policy
policy = st.secrets.get("DEFAULT_POLICY", "") + "\n" + st.session_state.get("custom_policy", "")

headers = {
    "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
    "Content-Type": "application/json"
}
prompt = f"Policy:\n{policy}\n\nQuestion: {query}"

payload = {
    "model": "mistralai/mixtral-8x7b-instruct",
    "messages": [
        {"role": "system", "content": "You are a professional Indian payroll assistant. Always give direct answers. If the answer is unknown, say 'Not available'."},
        {"role": "user", "content": prompt}
    ]
}

try:
    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
    reply = res.json()["choices"][0]["message"]["content"]
except:
    reply = "⚠️ Failed to get response."

st.session_state.chat_history.append(("bot", reply))

-------------- DISPLAY CHAT HISTORY --------------

for sender, msg in st.session_state.chat_history: style = "user-bubble" if sender == "user" else "bot-bubble" avatar = "🧑" if sender == "user" else "🤖" st.markdown(f"<div class='bubble {style}'><b>{avatar} {'You' if sender=='user' else 'Bot'}:</b><br>{msg}</div>", unsafe_allow_html=True)

-------------- FOOTER --------------

st.markdown("""

<center><small>Made with ❤️ by AC Creations | Powered by Streamlit + OpenRouter</small></center>
""", unsafe_allow_html=True)
