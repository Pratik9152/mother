import streamlit as st import requests import json from streamlit_lottie import st_lottie

Set app config

st.set_page_config(page_title="Smart Payroll Assistant", layout="centered")

🌈 Animated background + chatbot header

st.markdown("""

<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #00c9ff, #92fe9d, #f857a6, #ff5858);
    background-size: 500% 500%;
    animation: gradient 15s ease infinite;
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
.typing {
    width: 80px;
    height: 20px;
    background: rgba(255,255,255,0.4);
    border-radius: 50px;
    position: relative;
    animation: blink 1.5s infinite;
    margin: 5px auto;
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
    margin-top: 5px;
}
.send-button:hover {
    background-color: #0099cc;
}
.chat-bubble {
    max-width: 80%;
    padding: 12px;
    border-radius: 20px;
    margin: 8px;
    position: relative;
    color: #000;
    font-size: 15px;
    line-height: 1.4;
}
.user-bubble {
    background: #dcf8c6;
    align-self: flex-end;
    border-bottom-right-radius: 0;
    margin-left: auto;
}
.bot-bubble {
    background: #fff;
    align-self: flex-start;
    border-bottom-left-radius: 0;
    margin-right: auto;
}
.chat-container {
    display: flex;
    flex-direction: column;
}
.avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    margin-right: 8px;
    vertical-align: middle;
}
.bubble-row {
    display: flex;
    align-items: flex-end;
    margin-bottom: 10px;
}
</style>""", unsafe_allow_html=True)

Load animated bot

@st.cache_data(show_spinner=False) def load_lottie_url(url): r = requests.get(url) if r.status_code != 200: return None return r.json()

lottie_bot = load_lottie_url("https://lottie.host/f06a7f33-dff7-4d5a-a3b3-29cb765cd3f5/VHYJ6Ykr8G.json") if lottie_bot: st_lottie(lottie_bot, height=150, key="bot")

st.markdown("## 🤖 <span style='color:white;'>Smart Payroll Chatbot</span>", unsafe_allow_html=True) st.markdown("<p style='color:white; text-align:center;'>Ask anything about salary, PF, leave, F&F, bonus, and more!</p>", unsafe_allow_html=True)

Load default policy from secrets once

if "policy_data" not in st.session_state: st.session_state.policy_data = st.secrets.get("DEFAULT_POLICY", "")

Store chat

if "chat_history" not in st.session_state: st.session_state.chat_history = []

Admin panel for updating policy manually (optional)

with st.sidebar: st.subheader("🔐 Admin Login") password = st.text_input("Enter Admin Password", type="password") if password == st.secrets["ADMIN_PASSWORD"]: st.success("✅ Access Granted") policy_text = st.text_area("📝 Update Payroll Policy (Optional)", value=st.session_state.policy_data, height=300) if policy_text: st.session_state.policy_data = policy_text else: st.warning("Admin login required to update policy manually.")

Input first

query = st.text_input("", placeholder="Type your payroll question here...", key="chatbox")

Show chat history WhatsApp-style

for sender, msg in st.session_state.chat_history: if sender == "user": st.markdown(f""" <div class='bubble-row chat-container'> <div class='chat-bubble user-bubble'> <img src='https://cdn-icons-png.flaticon.com/512/1946/1946429.png' class='avatar'> <b>You:</b><br>{msg} </div> </div> """, unsafe_allow_html=True) else: st.markdown(f""" <div class='bubble-row chat-container'> <div class='chat-bubble bot-bubble'> <img src='https://cdn-icons-png.flaticon.com/512/4712/4712107.png' class='avatar'> <b>Bot:</b><br>{msg} </div> </div> """, unsafe_allow_html=True)

Then send button and typing animation

col1, col2 = st.columns([6, 1]) with col1: st.markdown("""<div class='typing'></div>""", unsafe_allow_html=True) with col2: send_clicked = st.button("Send", key="send", use_container_width=True)

Send query

if send_clicked and query: st.session_state.chat_history.append(("user", query)) policy = st.session_state.get("policy_data", "") headers = { "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}", "Content-Type": "application/json" } payload = { "model": "mistralai/mixtral-8x7b-instruct", "messages": [ { "role": "system", "content": "You are a smart payroll assistant. Answer directly and clearly from the company policy. Do not say 'as per policy'. Say 'Not mentioned' if unsure." }, {"role": "user", "content": f"Policy:\n{policy}\n\nQuestion: {query}"} ] } try: res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload)) reply = res.json()["choices"][0]["message"]["content"] except: reply = "⚠️ Unable to fetch reply. Check API or internet."

st.session_state.chat_history.append(("bot", reply))

