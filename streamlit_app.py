import streamlit as st import requests import json from streamlit_lottie import st_lottie

--- PAGE CONFIG ---

st.set_page_config(page_title="Smart Payroll Assistant", layout="centered")

--- STYLING ---

st.markdown("""

<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #6439ff, #ff4d6d);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
    font-family: 'Segoe UI', sans-serif;
    color: white;
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
.chat-bubble {
    padding: 12px;
    margin: 8px;
    max-width: 80%;
    border-radius: 12px;
    position: relative;
    font-size: 16px;
}
.user-bubble {
    background-color: #dcf8c6;
    color: #000;
    align-self: flex-end;
    border-bottom-right-radius: 0;
}
.bot-bubble {
    background-color: #ffffffb0;
    color: #000;
    align-self: flex-start;
    border-bottom-left-radius: 0;
}
.avatar {
    display: inline-block;
    width: 32px;
    height: 32px;
    background: #6f42c1;
    border-radius: 50%;
    text-align: center;
    line-height: 32px;
    color: white;
    font-weight: bold;
    margin-right: 6px;
}
.typing {
    width: 80px;
    height: 20px;
    background: rgba(255,255,255,0.4);
    border-radius: 50px;
    animation: blink 1.5s infinite;
    margin-left: 8px;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}
.send-button {
    background-color: #00c9ff;
    color: white;
    padding: 10px 24px;
    border: none;
    border-radius: 10px;
    font-weight: bold;
    cursor: pointer;
    transition: background-color 0.3s ease;
    width: 100%;
}
.send-button:hover {
    background-color: #0099cc;
}
</style>""", unsafe_allow_html=True)

--- ANIMATION ---

def load_lottie_url(url): r = requests.get(url) if r.status_code != 200: return None return r.json()

lottie_bot = load_lottie_url("https://lottie.host/f06a7f33-dff7-4d5a-a3b3-29cb765cd3f5/VHYJ6Ykr8G.json") if lottie_bot: st_lottie(lottie_bot, height=140, key="bot")

st.markdown("## 🤖 <span style='color:white;'>Payroll Assistant</span>", unsafe_allow_html=True) st.markdown("<p style='color:white; text-align:center;'>Ask about salary, PF, leave, F&F, and more!</p>", unsafe_allow_html=True)

--- CHAT STATE ---

if "chat_history" not in st.session_state: st.session_state.chat_history = []

--- CHAT INPUT ---

query = st.text_input("", placeholder="Type your payroll question here...", key="chatbox") send_clicked = st.button("Send", key="send", type="primary")

--- RESPONSE HANDLER ---

if send_clicked and query: st.session_state.chat_history.append(("user", query))

headers = {
    "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
    "Content-Type": "application/json"
}
prompt = st.secrets.get("DEFAULT_POLICY", "")
payload = {
    "model": "mistralai/mixtral-8x7b-instruct",
    "messages": [
        {
            "role": "system",
            "content": "You are a professional Indian payroll assistant. Respond clearly. Avoid phrases like 'as per policy'. If not found, say 'Not mentioned'."
        },
        {"role": "user", "content": f"Policy:

{prompt}

Question: {query}"} ] } try: res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload)) reply = res.json()["choices"][0]["message"]["content"] except: reply = "⚠️ Unable to fetch reply. Check your API key."

st.session_state.chat_history.append(("bot", reply))

--- DISPLAY MESSAGES ---

for sender, msg in st.session_state.chat_history: avatar = "<div class='avatar'>U</div>" if sender == 'user' else "<div class='avatar'>B</div>" bubble_class = "user-bubble" if sender == 'user' else "bot-bubble" st.markdown(f"<div style='display:flex;align-items:flex-start;margin-top:10px'>{avatar}<div class='chat-bubble {bubble_class}'>{msg}</div></div>", unsafe_allow_html=True)

