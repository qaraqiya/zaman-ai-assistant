import os
import json
import time
import pandas as pd
import streamlit as st
from assistent import record_voice, speech_to_text, ask_llm, speak

# === PAGE CONFIG ===
st.set_page_config(page_title="ZAMAN AI Assistant", page_icon="🌿", layout="wide")

st.markdown("""
    <style>
        body {background-color: #f9fafb;}
        .chat-message {padding: 12px; border-radius: 12px; margin-bottom: 10px; line-height: 1.4;}
        .user-msg {background-color: #DCF8C6; text-align: right;}
        .bot-msg {background-color: #EAEAEA; text-align: left;}
        .title {text-align: center; color: #1e293b;}
    </style>
""", unsafe_allow_html=True)

# === DATA LOAD ===
TRANSACTIONS_PATH = "/Users/kannursaya/Downloads/st/transactions.csv"
SEGMENTS_PATH = "/Users/kannursaya/Downloads/st/intent_segments_full.csv"

transactions_df = pd.read_csv(TRANSACTIONS_PATH)
segments_df = pd.read_csv(SEGMENTS_PATH)

transactions_df["date"] = pd.to_datetime(transactions_df["date"], errors="coerce")

# === USER PROFILE ===
def get_user_profile(user_id: int) -> dict:
    user_seg = segments_df[segments_df["user_id"] == user_id].to_dict(orient="records")
    user_tx = (
        transactions_df[transactions_df["user_id"] == user_id]
        .sort_values("date", ascending=False, na_position="last")
        .head(5)
        .to_dict(orient="records")
    )
    if not user_seg:
        return {"error": f"Пользователь {user_id} не найден в intent_segments_full.csv"}
    profile = user_seg[0]
    profile["recent_transactions"] = user_tx
    return profile

# === UI ===
st.markdown("<h1 class='title'>🌿 ZAMAN AI Assistant</h1>", unsafe_allow_html=True)
st.write("Ассистент, обученный принципам прозрачного исламского банкинга 💬")

user_id = st.number_input("Введите ваш User ID:", min_value=1, step=1)
profile = get_user_profile(user_id)

if "error" in profile:
    st.warning(profile["error"])
    st.stop()

st.subheader("📊 Профиль пользователя:")
st.json(profile)

# === CHAT ===
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Ассаламу алейкум 🌿 Чем могу помочь?"}
    ]

for msg in st.session_state["messages"]:
    role_class = "user-msg" if msg["role"] == "user" else "bot-msg"
    st.markdown(f"<div class='chat-message {role_class}'>{msg['content']}</div>", unsafe_allow_html=True)

user_input = st.chat_input("Введите сообщение...")

if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.spinner("Ассистент думает..."):
        prompt = f"Профиль пользователя: {json.dumps(profile, ensure_ascii=False)}\nВопрос: {user_input}"
        answer = ask_llm(prompt)
    st.session_state["messages"].append({"role": "assistant", "content": answer})
    st.rerun()

# === VOICE MODE ===
st.markdown("---")
st.markdown("## 🎧 Голосовой ассистент")

if "voice_text" not in st.session_state:
    st.session_state.voice_text = ""

col1, col2 = st.columns(2)
with col1:
    if st.button("🎙 Сказать голосом"):
        with st.spinner("🎙 Слушаю..."):
            filename = record_voice("voice_input.wav", duration=6)
            text = speech_to_text(filename)
            st.session_state.voice_text = text
            st.write(f"🗣 Вы сказали: {text}")

with col2:
    manual_text = st.text_input("💬 Или введите текст вручную:")
    if st.button("📨 Отправить"):
        st.session_state.voice_text = manual_text

if st.session_state.voice_text:
    st.markdown("### 🤖 Ответ ZAMAN Assistant:")
    full_prompt = f"Профиль пользователя: {json.dumps(profile, ensure_ascii=False)}\nВопрос: {st.session_state.voice_text}"
    reply = ask_llm(full_prompt)
    st.success(reply)

    if st.toggle("🔊 Озвучить ответ"):
        speak(reply)
