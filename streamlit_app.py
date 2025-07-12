import streamlit as st
import requests
import json
import fitz  # PyMuPDF
from streamlit_lottie import st_lottie

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="Payroll Assistant", layout="wide")

# ---------------------- LOAD LOTTIE ----------------------
def load_lottie_url(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

lottie_bot = load_lottie_url("https://lottie.host/f06a7f33-dff7-4d5a-a3b3-29cb765cd3f5/VHYJ6Ykr8G.json")

# ---------------------- STYLES ----------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #1f4037, #99f2c8, #a18cd1, #fbc2eb);
    background-size: 800% 800%;
    animation: gradientBG 30s ease infinite;
    font-family: 'Segoe UI', sans-serif;
    color: white;
    padding: 2rem;
}
@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
.message {
    padding: 12px 18px;
    border-radius: 18px;
    margin-bottom: 12px;
    max-width: 85%;
    display: inline-block;
    position: relative;
    word-wrap: break-word;
    font-size: 16px;
}
.bot-bubble {
    background: linear-gradient(145deg, #ffffff, #e6e6e6);
    color: #000;
    border-bottom-left-radius: 0;
    margin-left: 10px;
    box-shadow: 3px 3px 8px rgba(0,0,0,0.2);
    align-self: flex-start;
}
.user-bubble {
    background: linear-gradient(145deg, #25D366, #128C7E);
    color: white;
    border-bottom-right-radius: 0;
    margin-right: 10px;
    box-shadow: 3px 3px 8px rgba(0,0,0,0.2);
    align-self: flex-end;
    margin-left: auto;
}
.typing-animation {
    font-style: italic;
    color: #eeeeee;
    padding-left: 15px;
    animation: blink 1.5s infinite;
}
@keyframes blink {
    0%, 100% {opacity: 1;}
    50% {opacity: 0.4;}
}
</style>
""", unsafe_allow_html=True)

# ---------------------- HEADER ----------------------
if lottie_bot:
    st_lottie(lottie_bot, height=140, key="bot")
st.markdown("## 🤖 <span style='color:white;'>Payroll Assistant</span>", unsafe_allow_html=True)
st.markdown("<p style='color:white;'>Ask any question about salary, F&F, PF, tax, LTA, payroll law, ESIC, or Indian HR compliance.</p>", unsafe_allow_html=True)

# ---------------------- SESSION STATE ----------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_typing" not in st.session_state:
    st.session_state.is_typing = False

# ---------------------- DISPLAY CHAT ----------------------
for sender, msg in st.session_state.chat_history:
    role_class = "user-bubble" if sender == "user" else "bot-bubble"
    st.markdown(f"<div class='message {role_class}'><b>{'You' if sender=='user' else 'Bot'}:</b><br>{msg}</div>", unsafe_allow_html=True)

if st.session_state.is_typing:
    st.markdown("<div class='typing-animation'>Bot is typing...</div>", unsafe_allow_html=True)

# ---------------------- F&F PDF ANALYSIS ----------------------
st.markdown("### 📄 Upload F&F Statement (PDF) for Smart Check")
pdf_file = st.file_uploader("Upload F&F PDF", type="pdf")

if pdf_file:
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    pdf_text = "\n".join([page.get_text() for page in doc])
    st.session_state.chat_history.append(("user", "Analyze this full and final settlement statement as per company and Indian payroll policy:"))
    st.session_state.chat_history.append(("user", pdf_text))
    st.session_state.is_typing = True
    st.session_state.user_query = f"Analyze this full and final settlement:\n\n{pdf_text}"
    st.rerun()

# ---------------------- CHAT INPUT ----------------------
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("", placeholder="Type your payroll question here...", key="chatbox")
    send_click = st.form_submit_button("Send")

if send_click and user_input:
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.is_typing = True
    st.session_state.user_query = user_input
    st.rerun()

# ---------------------- API CALL ----------------------
if st.session_state.is_typing and "user_query" in st.session_state:
    query = st.session_state.user_query
    policy_text = st.secrets.get("DEFAULT_POLICY", "")

    headers = {
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {"role": "system", "content": "You are a payroll assistant trained on both the official company policy and Indian government payroll laws. Always answer clearly using both sources as reference.\n\n" + policy_text},
            {"role": "user", "content": query}
        ]
    }
    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload), timeout=15)
        reply = res.json()["choices"][0]["message"]["content"]
    except:
        reply = "⚠️ Sorry, something went wrong."

    st.session_state.chat_history.append(("bot", reply))
    st.session_state.is_typing = False
    del st.session_state.user_query
    st.rerun()

# ---------------------- PAYROLL TEAM INFO PAGE ----------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 👥 Payroll Team")
st.sidebar.markdown("**Head of Department:**\n- Shilpa Nimkar")
st.sidebar.markdown("**Managers:**\n- Shailesh Rane\n- Kanak Pawar")
st.sidebar.markdown("**Officer:**\n- Harshali Gawande")
st.sidebar.markdown("**Senior Assistant:**\n- Chinmay Sakharkar")
st.sidebar.markdown("**Assistant:**\n- Pratik Tekawade")

st.sidebar.markdown("---")
st.sidebar.markdown("For any escalations, contact the Payroll Team via official mail.")
