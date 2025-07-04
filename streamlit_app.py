import streamlit as st
import requests
import json
from streamlit_lottie import st_lottie

# ---------------- Page Setup ---------------- #
st.set_page_config(page_title="Smart Payroll Bot", layout="centered")

st.markdown("""
<style>
body {
    font-family: 'Segoe UI', sans-serif;
}
[data-testid="stAppViewContainer"] {
    background: linear-gradient(45deg, #9fbaa0, #1c92d2, #f2fcfe);
    background-size: 600% 600%;
    animation: gradient 20s ease infinite;
}
@keyframes gradient {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}
h1 {
    text-align: center;
    color: white;
    text-shadow: 1px 1px 3px black;
}
.bot-bubble {
    background-color: #e1ffc7;
    border-radius: 20px 20px 20px 5px;
    padding: 10px;
    margin: 5px 0;
    width: fit-content;
    max-width: 90%;
    display: flex;
    align-items: flex-start;
}
.user-bubble {
    background-color: #dcf8c6;
    border-radius: 20px 20px 5px 20px;
    padding: 10px;
    margin: 5px 0;
    align-self: flex-end;
    width: fit-content;
    max-width: 90%;
}
.avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    margin-right: 8px;
}
.chat-row {
    display: flex;
    align-items: flex-start;
}
.user .chat-row {
    justify-content: flex-end;
}
.typing {
    margin-top: 5px;
    font-size: 12px;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# --------- Load Animation --------- #
def load_lottie_url(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_bot = load_lottie_url("https://lottie.host/f06a7f33-dff7-4d5a-a3b3-29cb765cd3f5/VHYJ6Ykr8G.json")
if lottie_bot:
    st_lottie(lottie_bot, height=160, key="paybot")

st.markdown("<h1>🤖 Smart Payroll Chatbot</h1>", unsafe_allow_html=True)

# ------------- Admin Panel ------------ #
with st.sidebar:
    st.subheader("🔐 Admin Panel")
    pwd = st.text_input("Admin Password", type="password")
    if pwd == st.secrets["ADMIN_PASSWORD"]:
        st.success("Access Granted")
        policy = st.text_area("✍️ Update Payroll Policy", height=300)
        if policy:
            st.session_state["policy"] = policy

# ------------- Load Policy ------------- #
if "policy" not in st.session_state:
    st.session_state["policy"] = st.secrets["DEFAULT_POLICY"]

# ------------- Chat History ------------- #
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

query = st.text_input("💬 Ask Payroll Question", placeholder="e.g., Who is payroll HOD?")

if st.button("Send") and query:
    st.session_state.chat_history.append(("user", query))

    headers = {
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }
    prompt = st.session_state["policy"]

    payload = {
        "model": "mistralai/mixtral-8x7b-instruct",
        "messages": [
            {"role": "system", "content": "You are a smart payroll assistant. Answer directly using the given policy. Never say 'as per policy'. If not found, say 'Not mentioned'."},
            {"role": "user", "content": f"Policy:\n{prompt}\n\nQuestion: {query}"}
        ]
    }

    try:
        res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload))
        reply = res.json()["choices"][0]["message"]["content"]
    except:
        reply = "⚠️ API error. Try again."

    st.session_state.chat_history.append(("bot", reply))

# ---------- Chat UI (WhatsApp style) ---------- #
for sender, msg in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"""
        <div class="user chat-row">
            <div class="user-bubble">{msg}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="chat-row">
            <img src="https://cdn-icons-png.flaticon.com/512/4712/4712107.png" class="avatar"/>
            <div class="bot-bubble">{msg}</div>
        </div>
        """, unsafe_allow_html=True)
