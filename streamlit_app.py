import streamlit as st
import requests
import json 
from streamlit_lottie import st_lottie 
from datetime import datetime

---------- PAGE CONFIGURATION ----------

st.set_page_config( page_title="Smart Payroll Assistant | AC Creations", page_icon="🧠", layout="wide" )

---------- CUSTOM STYLES ----------

st.markdown("""

<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap');

html, body, [data-testid="stAppViewContainer"]  {
    font-family: 'Montserrat', sans-serif;
    background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364);
    background-size: 400% 400%;
    animation: gradient 20s ease infinite;
    color: white;
    scroll-behavior: smooth;
}

@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

h1, h2, h3, h4 {
    color: #ffffff;
    text-align: center;
    text-shadow: 2px 2px 8px #00000090;
}

.chat-container {
    max-height: 60vh;
    overflow-y: auto;
    padding-right: 10px;
    margin-bottom: 20px;
}

.chat-bubble {
    padding: 12px 20px;
    border-radius: 25px;
    margin-bottom: 10px;
    max-width: 80%;
    word-wrap: break-word;
    box-shadow: 0 0 10px rgba(255,255,255,0.15);
    position: relative;
    animation: fadeIn 0.4s ease-in-out;
}

.user-bubble {
    background-color: #2ecc71;
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 0;
}

.bot-bubble {
    background-color: #fff;
    color: black;
    align-self: flex-start;
    border-bottom-left-radius: 0;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.input-row {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
}

input[type="text"] {
    flex: 1;
    padding: 12px;
    border-radius: 10px;
    border: none;
    font-size: 16px;
    margin-right: 10px;
    background-color: #ffffff10;
    color: white;
}

button {
    background-color: #9b59b6;
    color: white;
    border: none;
    padding: 12px 20px;
    border-radius: 10px;
    font-size: 16px;
    font-weight: bold;
    cursor: pointer;
    transition: background 0.3s;
}

button:hover {
    background-color: #8e44ad;
}
</style>""", unsafe_allow_html=True)

---------- LOAD ANIMATION ----------

def load_lottie_url(url): r = requests.get(url) if r.status_code != 200: return None return r.json()

lottie_bot = load_lottie_url("https://lottie.host/f06a7f33-dff7-4d5a-a3b3-29cb765cd3f5/VHYJ6Ykr8G.json") if lottie_bot: st_lottie(lottie_bot, height=150, key="bot")

st.markdown("<h1>🤖 Smart Payroll Chatbot</h1>", unsafe_allow_html=True) st.markdown("<p style='color:white; text-align:center;'>Ask anything about salary, PF, leave, F&F, bonus, and more!</p>", unsafe_allow_html=True)

---------- CHAT STORAGE ----------

if "chat_history" not in st.session_state: st.session_state.chat_history = []

---------- ADMIN PANEL (Update Policy) ----------

with st.sidebar: st.subheader("🔐 Admin Panel") password = st.text_input("Enter Admin Password", type="password") if password == st.secrets["ADMIN_PASSWORD"]: st.success("✅ Access Granted") policy_text = st.text_area("📝 Enter or Paste Payroll Policy", height=300) if policy_text: st.session_state["policy_data"] = policy_text else: st.info("Enter password to unlock policy access.")

---------- CHAT UI (Display History) ----------

st.markdown("<div class='chat-container'>", unsafe_allow_html=True) for role, msg in st.session_state.chat_history: css_class = "user-bubble" if role == "user" else "bot-bubble" avatar = "<div class='avatar'>You</div>" if role == 'user' else "<div class='avatar'>Bot</div>" st.markdown(f"<div class='input-row'>{avatar}<div class='chat-bubble {css_class}'>{msg}</div></div>", unsafe_allow_html=True) st.markdown("</div>", unsafe_allow_html=True)

---------- CHAT INPUT AT BOTTOM ----------

query = st.text_input("💬 Ask Payroll Questions Here...") if st.button("Send", key="send", use_container_width=True) and query: st.session_state.chat_history.append(("user", query))

headers = {
    "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
    "Content-Type": "application/json"
}
prompt = st.session_state.get("policy_data", st.secrets.get("DEFAULT_POLICY", ""))
payload = {
    "model": "mistralai/mixtral-8x7b-instruct",
    "messages": [
        {"role": "system", "content": "You are a payroll assistant. Respond with clear, friendly answers. If unsure, say 'Not available'."},
        {"role": "user", "content": f"Policy:\n{prompt}\n\nQuestion: {query}"}
    ]
}
try:
    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
    reply = res.json()["choices"][0]["message"]["content"]
except:
    reply = "⚠️ Failed to get response. Check API key."

st.session_state.chat_history.append(("bot", reply))

