import streamlit as st import requests import json from streamlit_lottie import st_lottie

Set page configuration

st.set_page_config(page_title="Smart Payroll Chatbot", layout="centered")

Custom styles: 3D gradient background, typing animation, bubble tails

st.markdown("""

<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(120deg, #2C5364, #203A43, #0F2027);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
    font-family: 'Segoe UI', sans-serif;
    padding: 2rem;
    color: white;
    overflow-x: hidden;
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
    background-color: #f1f0f0;
    color: #000;
    align-self: flex-start;
    border-bottom-left-radius: 0;
    margin-right: auto;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    margin-left: 10px;
}
.user-bubble {
    background-color: #25D366;
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 0;
    margin-left: auto;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    margin-right: 10px;
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
.typing-animation {
    font-style: italic;
    color: #ccc;
    padding-left: 15px;
    animation: blink 1.5s infinite;
}
@keyframes blink {
    0%, 100% {opacity: 1;}
    50% {opacity: 0.4;}
}
</style>""", unsafe_allow_html=True)

Lottie animation for header

def load_lottie_url(url): r = requests.get(url) if r.status_code != 200: return None return r.json()

lottie_bot = load_lottie_url("https://lottie.host/f06a7f33-dff7-4d5a-a3b3-29cb765cd3f5/VHYJ6Ykr8G.json") if lottie_bot: st_lottie(lottie_bot, height=150, key="bot")

st.markdown("## 🤖 <span style='color:white;'>Smart Payroll Chatbot</span>", unsafe_allow_html=True) st.markdown("<p style='color:white;'>Ask anything related to Indian payroll: PF, LTA, gratuity, F&F, bonus, salary.</p>", unsafe_allow_html=True)

Admin panel

with st.sidebar: st.subheader("🔐 Admin Login") password = st.text_input("Enter Admin Password", type="password") if password == st.secrets["ADMIN_PASSWORD"]: st.success("✅ Access Granted") policy_text = st.text_area("📝 Paste Additional Payroll Policy", height=300) if policy_text: st.session_state["policy_data"] = policy_text else: st.warning("Admin login required to edit policy.")

Chat history state

if "chat_history" not in st.session_state: st.session_state.chat_history = [] if "is_typing" not in st.session_state: st.session_state.is_typing = False

Floating input at bottom

with st.container(): st.markdown("<div class='input-container'>", unsafe_allow_html=True) user_input = st.text_input("", placeholder="Type your payroll question...", key="chatbox_fixed") send_click = st.button("Send", key="send_fixed") st.markdown("</div>", unsafe_allow_html=True)

if send_click and user_input: st.session_state.chat_history.append(("user", user_input)) st.session_state.is_typing = True st.experimental_rerun()

Display chat

for sender, msg in st.session_state.chat_history: role_class = "user-bubble" if sender == "user" else "bot-bubble" st.markdown(f"<div class='message {role_class}'><b>{'You' if sender=='user' else 'Bot'}:</b><br>{msg}</div>", unsafe_allow_html=True)

Typing indicator

if st.session_state.is_typing: st.markdown("<div class='typing-animation'>Bot is typing...</div>", unsafe_allow_html=True) query = st.session_state.chat_history[-1][1] combined_policy = f"{st.secrets.get('DEFAULT_POLICY', '')}\n{st.session_state.get('policy_data', '')}" headers = { "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}", "Content-Type": "application/json" } payload = { "model": "mistralai/mixtral-8x7b-instruct", "messages": [ {"role": "system", "content": "You are a smart Indian payroll assistant. Be clear. No 'as per policy'."}, {"role": "user", "content": f"Policy:\n{combined_policy}\n\nQuestion: {query}"} ] } try: res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload), timeout=15) reply = res.json()["choices"][0]["message"]["content"] except: reply = "⚠️ Could not respond."

st.session_state.chat_history.append(("bot", reply))
st.session_state.is_typing = False
st.experimental_rerun()

