import streamlit as st import requests import json from streamlit_lottie import st_lottie

---------------------- CONFIG ----------------------

st.set_page_config(page_title="Smart Payroll Chatbot", layout="centered")

---------------------- STYLES ----------------------

st.markdown("""

<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(-45deg, #fc466b, #3f5efb, #43e97b, #38f9d7);
    background-size: 600% 600%;
    animation: gradientBG 20s ease infinite;
    font-family: 'Segoe UI', sans-serif;
    padding-bottom: 8rem;
    color: white;
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
    align-self: flex-start;
    border-bottom-left-radius: 0;
    margin-right: auto;
    box-shadow: 3px 3px 8px rgba(0,0,0,0.2);
    margin-left: 10px;
}
.user-bubble {
    background: linear-gradient(145deg, #25D366, #128C7E);
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 0;
    margin-left: auto;
    box-shadow: 3px 3px 8px rgba(0,0,0,0.2);
    margin-right: 10px;
}
.input-container {
    position: fixed;
    bottom: 1.5rem;
    left: 2rem;
    right: 2rem;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 15px;
    padding: 12px;
    backdrop-filter: blur(6px);
    z-index: 999;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 0 10px rgba(0,0,0,0.3);
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
input[type="text"] {
    flex-grow: 1;
    padding: 10px;
    border-radius: 10px;
    border: none;
    font-size: 16px;
    margin-right: 10px;
    color: #000;
}
button[kind="primary"] {
    background-color: #00BFA6 !important;
    color: white !important;
    border-radius: 10px;
    font-weight: bold;
    padding: 8px 18px;
    border: none;
}
</style>""", unsafe_allow_html=True)

---------------------- HEADER ----------------------

def load_lottie_url(url): r = requests.get(url) if r.status_code != 200: return None return r.json()

lottie_bot = load_lottie_url("https://lottie.host/f06a7f33-dff7-4d5a-a3b3-29cb765cd3f5/VHYJ6Ykr8G.json") if lottie_bot: st_lottie(lottie_bot, height=150, key="bot")

st.markdown("## 🤖 <span style='color:white;'>Smart Payroll Chatbot</span>", unsafe_allow_html=True) st.markdown("<p style='color:white;'>Ask about PF, F&F, Gratuity, Bonus, Salary, LTA etc.</p>", unsafe_allow_html=True)

---------------------- SIDEBAR ADMIN ----------------------

with st.sidebar: st.subheader("🔐 Admin Login") password = st.text_input("Enter Admin Password", type="password") if password == st.secrets["ADMIN_PASSWORD"]: st.success("✅ Access Granted") policy_text = st.text_area("📝 Add Payroll Policy (optional)", height=300) if policy_text: st.session_state["extra_policy"] = policy_text else: st.warning("Admin login required to update policy.")

---------------------- SESSION INIT ----------------------

if "chat_history" not in st.session_state: st.session_state.chat_history = [] if "extra_policy" not in st.session_state: st.session_state.extra_policy = ""

---------------------- INPUT BOX ----------------------

st.markdown("<div class='input-container'>", unsafe_allow_html=True) query = st.text_input("", placeholder="Type your payroll question here...", key="chatbox") send = st.button("Send") st.markdown("</div>", unsafe_allow_html=True)

---------------------- HANDLE MESSAGE ----------------------

if send and query: st.session_state.chat_history.append(("user", query))

policy_combined = st.secrets.get("DEFAULT_POLICY", "") + "\n" + st.session_state.get("extra_policy", "")
headers = {
    "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
    "Content-Type": "application/json"
}
payload = {
    "model": "mistralai/mixtral-8x7b-instruct",
    "messages": [
        {
            "role": "system",
            "content": "You are a smart Indian payroll assistant. Be very clear. Don't say 'as per policy'. If nothing is found, still try your best based on Indian payroll knowledge."
        },
        {"role": "user", "content": f"Policy:\n{policy_combined}\n\nQuestion: {query}"}
    ]
}

try:
    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload), timeout=20)
    reply = res.json()["choices"][0]["message"]["content"]
except:
    reply = "⚠️ Could not fetch reply."

st.session_state.chat_history.append(("bot", reply))
st.experimental_rerun()

---------------------- DISPLAY CHAT ----------------------

for sender, msg in st.session_state.chat_history: css = "user-bubble" if sender == "user" else "bot-bubble" st.markdown(f"<div class='message {css}'><b>{'You' if sender=='user' else 'Bot'}:</b><br>{msg}</div>", unsafe_allow_html=True)

---------------------- AUTOSCROLL ----------------------

st.markdown("""

<script>
window.scrollTo(0, document.body.scrollHeight);
</script>""", unsafe_allow_html=True)

