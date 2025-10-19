import streamlit as st
from datetime import datetime

# ---------- GLOBAL STYLE ----------
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: "Inter", sans-serif;
    color: #1a1a1a;
    background: linear-gradient(135deg, #EEFE6D 0%, #F8FFF3 40%, #E9FFF7 70%, #2D9A86 100%) fixed;
}
.chat-container {
    background: rgba(255,255,255,0.6);
    border: 1px solid rgba(45,154,134,0.25);
    backdrop-filter: blur(16px);
    border-radius: 30px;
    box-shadow: 0 10px 40px rgba(45,154,134,0.15);
    padding: 2rem;
    max-width: 750px;
    margin: 2rem auto;
    height: 20vh;
    display: flex;
    flex-direction: column;
}
.messages {
    flex: 1;
    overflow-y: auto;
    padding-right: 1rem;
    margin-bottom: 1rem;
}
.message {
    padding: 0.8rem 1.2rem;
    border-radius: 20px;
    margin-bottom: 0.7rem;
    max-width: 80%;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.user {
    align-self: flex-end;
    background: #2D9A86;
    color: white;
    border-bottom-right-radius: 5px;
}
.bot {
    align-self: flex-start;
    background: rgba(255,255,255,0.85);
    border-bottom-left-radius: 5px;
    border: 1px solid rgba(45,154,134,0.2);
}
input, textarea {
    border-radius: 20px !important;
}
.send-btn button {
    background-color: #2D9A86 !important;
    color: white !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
    padding: 0.6em 1.4em !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<style>
/* remove the grey top bar / header */
header[data-testid="stHeader"] {
    display: none !important;
}

/* remove top padding Streamlit adds after hiding header */
main.block-container {
    padding-top: 1rem !important;
}

/* remove bottom padding */
main.block-container {
    padding-bottom: 0rem !important;
}

/* optional: make background transparent inside iframe */
section.main {
    background-color: transparent !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "text": "Салем! Я — Abu. Чем могу помочь сегодня?"}
    ]

# ---------- CHAT AREA ----------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
st.markdown('<div class="messages">', unsafe_allow_html=True)

for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(f"<div class='message user'>{msg['text']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='message bot'>{msg['text']}</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------- INPUT ----------
with st.form("chat_form", clear_on_submit=True):
    cols = st.columns([8, 2])
    user_input = cols[0].text_input("Введите сообщение...", placeholder="Например: Рассчитай вклад на 12 месяцев")
    send = cols[1].form_submit_button("Отправить")

if send and user_input:
    st.session_state["messages"].append({"role": "user", "text": user_input})
    
    # TEMPORARY placeholder logic (replace later with real model)
    fake_reply = f"Ответ от Abu: обработка запроса «{user_input}»... (здесь появится реальный ответ ML модели)"
    st.session_state["messages"].append({"role": "assistant", "text": fake_reply})
    st.experimental_rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ---------- FOOTER ----------
st.markdown("""
<div style='text-align:center; padding:1rem; color:#666; font-size:0.9rem;'>
© 2025 Sabinia.csv — Powered by Streamlit + Zamanbank Hackathon
</div>
""", unsafe_allow_html=True)