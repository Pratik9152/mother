import streamlit as st import requests import json from streamlit_lottie import st_lottie

Set page configuration

st.set_page_config(page_title="Smart Payroll Chatbot", layout="centered")

Custom styles: WhatsApp-style UI, animated background, better colors

st.markdown("""

<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #1a1a2e, #16213e, #0f3460);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
    font-family: 'Segoe UI', sans-serif;
    color: white;
    padding: 2rem;
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
    max-width: 80%;
    display: inline-block;
    position: relative;
    word-wrap: break-word;
    font-size: 16px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
}
.user-bubble {
    background-color: #25D366;
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 0;
    margin-left: auto;
    text-align: right;
}
.bot-bubble {
    background-color: #e4e6eb;
    color: black;
    align-self: flex-start;
    border-bottom-left-radius: 0;
    margin-right: auto;
    text-align: left;
}
.input-box {
    position: fixed;
    bottom: 1rem;
    left: 1rem;
    right: 1rem;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(5px);
    padding: 10px;
    border-radius: 10px;
    z-index: 999;
    display: flex;
    gap: 10px;
}
.stTextInput>div>input {
    padding: 10px;
    border-radius: 10px;
    border: none;
    width: 100%;
}
.stButton>button {
    background-color: #25D366;
    color: white;
    font-weight: bold;
    border: none;
    padding: 10px 20px;
    border-radius: 10px;
    cursor: pointer;
}
.stButton>button:hover {
    background-color: #128C7E;
}
</style>""", unsafe_allow_html=True)

Header Lottie

def load_lottie_url(url): r = requests.get(url) if r.status_code != 200: return None return r.json()

lottie_bot = load_lottie_url("https://lottie.host/f06a7f33-dff7-4d5a-a3b3-29cb765cd3f5/VHYJ6Ykr8G.json") if lottie_bot: st_lottie(lottie_bot, height=140, key="bot")

st.markdown("## 🤖 <span style='color:white;'>Smart Payroll Chatbot</span>", unsafe_allow_html=True) st.markdown("<p style='color:white;'>Ask anything related to salary, PF, bonus, leave, or F&F!</p>", unsafe_allow_html=True)

Admin panel

with st.sidebar: st.subheader("🔐 Admin Login") password = st.text_input("Enter Admin Password", type="password") if password == st.secrets["ADMIN_PASSWORD"]: st.success("✅ Access Granted") policy_text = st.text_area("📝 Paste Additional Payroll Policy", height=300) if policy_text: st.session_state["policy_data"] = policy_text else: st.warning("Admin login required to edit policy.")

Chat state

if "chat_history" not in st.session_state: st.session_state.chat_history = []

Chat display

for sender, msg in st.session_state.chat_history: bubble = "user-bubble" if sender == "user" else "bot-bubble" st.markdown(f"<div class='message {bubble}'><b>{'You' if sender=='user' else 'Bot'}:</b><br>{msg}</div>", unsafe_allow_html=True)

Input + button at bottom

st.markdown("<div class='input-box'>", unsafe_allow_html=True) col1, col2 = st.columns([8, 2]) with col1: user_input = st.text_input("", placeholder="Type your payroll question here...", key="chat_input") with col2: send_click = st.button("Send") st.markdown("</div>", unsafe_allow_html=True)

if send_click and user_input: st.session_state.chat_history.append(("user", user_input))

base_policy = st.secrets.get("DEFAULT_POLICY", "")
admin_policy = st.session_state.get("policy_data", "")
combined_policy = f"{base_policy}\n{admin_policy}".strip()

headers = {
    "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
    "Content-Type": "application/json"
}
payload = {
    "model": "mistralai/mixtral-8x7b-instruct",
    "messages": [
        {
            "role": "system",
            "content": "You are a helpful Indian payroll assistant. Only answer payroll-related questions."
        },
        {
            "role": "user",
            "content": f"Policy:\n{combined_policy}\n\nQuestion: {user_input}"
        }
    ]
}

try:
    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload), timeout=10)
    reply = res.json()["choices"][0]["message"]["content"]
except:
    reply = "⚠️ Unable to fetch response."

st.session_state.chat_history.append(("bot", reply))

st.experimental_rerun()

