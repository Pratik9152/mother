import streamlit as st
import requests
import json
from streamlit_lottie import st_lottie
from datetime import datetime

# ---------- PAGE CONFIGURATION ---------- #
st.set_page_config(
    page_title="Smart Payroll Assistant | AC Creations",
    page_icon="🧠",
    layout="wide"
)

# ---------- CUSTOM STYLES ---------- #
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600&display=swap');

html, body, [data-testid="stAppViewContainer"]  {
    font-family: 'Montserrat', sans-serif;
    background: linear-gradient(-45deg, #1f1c2c, #928dab, #1f1c2c);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
    color: white;
}

@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

h1, h2, h3, h4 {
    color: #fff;
    text-align: center;
    text-shadow: 2px 2px 8px #00000090;
}

.chatbox {
    background-color: rgba(255,255,255,0.05);
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 10px;
    box-shadow: 0 0 10px rgba(255,255,255,0.1);
    font-size: 17px;
}

.bot { background-color: rgba(0,255,200,0.1); }
.user { background-color: rgba(255,0,180,0.1); }

.footer {
    text-align: center;
    font-size: 14px;
    margin-top: 40px;
    opacity: 0.6;
}

input, textarea, button {
    border-radius: 10px !important;
    font-size: 16px !important;
}

.stTextInput>div>div>input {
    background-color: rgba(255,255,255,0.15);
    color: white;
}

</style>
""", unsafe_allow_html=True)

# ---------- ANIMATION ---------- #
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_url = "https://lottie.host/f06a7f33-dff7-4d5a-a3b3-29cb765cd3f5/VHYJ6Ykr8G.json"
chat_lottie = load_lottie_url(lottie_url)

# ---------- HEADER ---------- #
with st.container():
    st_lottie(chat_lottie, height=200)
    st.markdown("""
        <h1>Smart Payroll Assistant</h1>
        <h4>Ask me anything related to payroll. I'm trained on your company policy!</h4>
    """, unsafe_allow_html=True)

# ---------- SIDEBAR (Admin Panel) ---------- #
with st.sidebar:
    st.header("🔐 Admin Panel")
    password = st.text_input("Enter Admin Password", type="password")
    if password == st.secrets["ADMIN_PASSWORD"]:
        st.success("Admin Access Granted")
        policy_text = st.text_area("Paste your company payroll policy below:", height=300)
        if policy_text:
            st.session_state["policy"] = policy_text
    else:
        st.info("Enter password to unlock policy access.")

# ---------- CHAT STORAGE ---------- #
if "chat" not in st.session_state:
    st.session_state.chat = []

# ---------- MAIN CHAT INPUT ---------- #
st.markdown("---")
query = st.text_input("💬 Type your question", placeholder="e.g. What is the PF deduction?", key="question")
if st.button("Send") and query:
    st.session_state.chat.append(("user", query))

    headers = {
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }
    prompt = st.session_state.get("policy", "")
    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {"role": "system", "content": "You are a smart payroll assistant. Always give direct professional answers. Never say 'as per policy'. If unsure, reply 'Not available'."},
            {"role": "user", "content": f"Policy:\n{prompt}\n\nQuestion: {query}"}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
        answer = response.json()["choices"][0]["message"]["content"]
    except:
        answer = "⚠️ Failed to get response. Check your API key."

    st.session_state.chat.append(("bot", answer))

# ---------- DISPLAY CHAT ---------- #
for role, message in st.session_state.chat:
    css_class = "user" if role == "user" else "bot"
    st.markdown(f"<div class='chatbox {css_class}'><b>{'You' if role=='user' else 'Bot'}:</b> {message}</div>", unsafe_allow_html=True)

# ---------- FOOTER ---------- #
st.markdown("""
<div class='footer'>
    © 2025 AC Creations | Powered by Streamlit + OpenRouter | Chat rendered on: {}
</div>
""".format(datetime.now().strftime("%B %d, %Y %H:%M")), unsafe_allow_html=True)
