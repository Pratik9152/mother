import streamlit as st
import requests
import json
import PyPDF2
from streamlit_lottie import st_lottie
import base64
from deep_translator import GoogleTranslator
import time

# ---------------------- PAGE CONFIG ----------------------
st.set_page_config(page_title="Payroll Assistant", layout="wide")

# ---------------------- CUSTOM SCROLL ANCHOR ----------------------
st.markdown("""
<script>
function scrollToBottom() {
    var chat = window.parent.document.querySelector('.main');
    if(chat) chat.scrollTop = chat.scrollHeight;
}
window.addEventListener("load", scrollToBottom);
setTimeout(scrollToBottom, 800);
</script>
""", unsafe_allow_html=True)

# ---------------------- STYLES ----------------------
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #ff9a9e, #fad0c4, #fbc2eb, #a6c1ee);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    font-family: 'Segoe UI', sans-serif;
    color: white;
    padding: 2rem;
    overflow-x: hidden;
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
    animation: fadeIn 0.3s ease-in-out;
}
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
.bot-bubble {
    background: #f0f0f0;
    color: #000;
    border-bottom-left-radius: 0;
    margin-left: 10px;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.1);
    align-self: flex-start;
}
.user-bubble {
    background: linear-gradient(145deg, #25D366, #128C7E);
    color: white;
    border-bottom-right-radius: 0;
    margin-right: 10px;
    box-shadow: 2px 2px 6px rgba(0,0,0,0.1);
    align-self: flex-end;
    margin-left: auto;
}
.typing-animation {
    display: inline-block;
    margin-left: 12px;
    animation: blink 1.5s infinite;
    color: #eeeeee;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}
.stTextInput > div > div > input {
    background-color: #fff;
    color: black;
}
.stButton button {
    background: #25D366 !important;
    border: none;
    color: white;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ---------------------- HEADER ----------------------
st.markdown("## 🤖 <span style='color:white;'>Payroll Assistant</span>", unsafe_allow_html=True)
st.markdown("<p style='color:white;'>Ask in any language — I’ll answer everything about PF, LTA, F&F, Salary, or Gratuity.</p>", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "is_typing" not in st.session_state:
    st.session_state.is_typing = False
if "chatbox" not in st.session_state:
    st.session_state.chatbox = ""

# ---------------------- CHAT DISPLAY ----------------------
for sender, msg in st.session_state.chat_history:
    role_class = "user-bubble" if sender == "user" else "bot-bubble"
    st.markdown(f"<div class='message {role_class}'><b>{'You' if sender=='user' else 'Bot'}:</b><br>{msg}</div>", unsafe_allow_html=True)
if st.session_state.is_typing:
    st.markdown("<div class='typing-animation'>🤖 Bot is typing...</div>", unsafe_allow_html=True)

# ---------------------- CHAT INPUT ----------------------
col1, col2 = st.columns([6, 1])
with col1:
    user_input = st.text_input("", placeholder="Type your payroll question here...", key="chatbox")
with col2:
    send_clicked = st.button("Send")

# ---------------------- SMART FNF DETECT ----------------------
if user_input and ("fnf" in user_input.lower() or "full and final" in user_input.lower()):
    st.markdown("### 📎 Upload your Full & Final Statement for analysis")
    pdf_file = st.file_uploader("Upload PDF", type="pdf")
    if pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        pdf_text = "\n".join([page.extract_text() or "" for page in reader.pages])
        st.session_state.chat_history.append(("user", "Analyze this full and final settlement:"))
        st.session_state.chat_history.append(("user", pdf_text))
        st.session_state.user_query = f"Analyze this full and final settlement:\n\n{pdf_text}"
        st.session_state.is_typing = True
        st.rerun()

# ---------------------- API CALL ----------------------
if send_clicked and user_input.strip():
    query = user_input.strip()
    st.session_state.chat_history.append(("user", query))
    st.session_state.is_typing = True
    st.session_state.user_query = query
    st.session_state.chatbox = ""
    st.rerun()

if st.session_state.is_typing and "user_query" in st.session_state:
    query = st.session_state.user_query.strip()
    policy_text = st.secrets.get("DEFAULT_POLICY", "")

    try:
        translator = GoogleTranslator(source='auto', target='en')
        translated_query = translator.translate(query)
        user_lang = translator.source
    except:
        translated_query = query
        user_lang = "en"

    time.sleep(1.2)

    if query.lower() in ["hi", "hello", "hey", "ok", "okay"]:
        reply = "👋 Hello! I'm your Payroll Assistant. Ask me anything about salary, PF, tax, or Full & Final."
    else:
        headers = {
            "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "mistralai/mixtral-8x7b-instruct",
            "messages": [
                {"role": "system", "content": "You are a smart payroll assistant trained on company and Indian payroll policy. Answer briefly and clearly. Avoid repeating full policies unless asked.\n" + policy_text},
                {"role": "user", "content": translated_query}
            ]
        }
        try:
            res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload), timeout=15)
            reply = res.json()["choices"][0]["message"]["content"]
            if user_lang != "en":
                reply = GoogleTranslator(source='en', target=user_lang).translate(reply)
        except:
            reply = "⚠️ Sorry, something went wrong."

    st.session_state.chat_history.append(("bot", reply))
    st.session_state.is_typing = False
    del st.session_state.user_query
    st.rerun()

# ---------------------- SIDEBAR ----------------------
st.sidebar.markdown("---")
st.sidebar.markdown("### 👥 Payroll Team")
st.sidebar.markdown("**HOD:** Shilpa Nimkar")
st.sidebar.markdown("**Managers:**\n- Shailesh Rane\n- Kanak Pawar")
st.sidebar.markdown("**Officer:** Harshali Gawande")
st.sidebar.markdown("**Sr. Assistant:** Chinmay Sakharkar")
st.sidebar.markdown("**Assistant:** Pratik Tekawade")
st.sidebar.markdown("---")
st.sidebar.markdown("💬 Ask me anything about salary, PF, tax, reimbursements, F&F, or ESIC. Available in Hindi, Marathi, or English.")
