import os
import json
import sounddevice as sd
import soundfile as sf
import requests
from gtts import gTTS
import warnings
import urllib3
import playsound

# =========================
# ⚙️ CONFIGURATION
# =========================

# 🔇 Отключаем предупреждения от urllib3 (LibreSSL)
warnings.filterwarnings("ignore", category=UserWarning)
urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)

# 🔑 API ключ (создай на https://platform.openai.com/api-keys)
OPENAI_KEY = "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"
# 🔗 API endpoints
LLM_URL = "https://api.openai.com/v1/chat/completions"
WHISPER_URL = "https://api.openai.com/v1/audio/transcriptions"

# 🧾 Заголовки для запросов
HEADERS_JSON = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_KEY}"
}
HEADERS_WHISPER = {
    "Authorization": f"Bearer {OPENAI_KEY}"
}

# =========================
# 🎙️ RECORD VOICE
# =========================
def record_voice(filename="voice.wav", duration=6):
    print("🎙️ Говори, я слушаю...")
    sr = 44100
    audio = sd.rec(int(duration * sr), samplerate=sr, channels=1, dtype="float32")
    sd.wait()
    sf.write(filename, audio, sr)
    print("✅ Записано!")
    return filename

# =========================
# 🔊 SPEECH → TEXT (Whisper)
# =========================
def speech_to_text(filename):
    print("🔊 Распознаю речь (через Whisper)...")
    try:
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "audio/wav")}
            data = {"model": "whisper-1", "language": "ru"}
            r = requests.post(WHISPER_URL, headers=HEADERS_WHISPER, files=files, data=data)
            r.raise_for_status()
            result = r.json()
            text = result.get("text", "").strip()
            print(f"🗣️ Ты сказал(а): {text}")
            return text
    except Exception as e:
        print(f"⚠️ Ошибка Whisper: {e}")
        return ""

# =========================
# 🔈 TEXT → VOICE (gTTS)
# =========================
def speak(text, filename="reply.mp3"):
    """Convert text to speech and play it."""
    print("🔊 Озвучиваю ответ...")
    try:
        tts = gTTS(text=text, lang="ru")
        tts.save(filename)
        playsound.playsound(filename)
        os.remove(filename)
    except Exception as e:
        print(f"⚠️ Ошибка TTS: {e}")

# =========================
# 🧠 GPT-4 (Chat Assistant)
# =========================
def ask_llm(prompt):
    try:
        system_context = [
            {
                "role": "system",
                "content": (
                    "Ты — интеллектуальный банковский ассистент ZAMAN Bank — первого исламского цифрового банка Казахстана. "
                    "Помогаешь людям понимать исламские финансовые продукты, рассчитывать платежи и давать советы. "
                    "Говори дружелюбно, с уважением и лёгким теплом ."
                )
            },
            {
                "role": "system",
                "content": (
                    "Информация о банке: ZAMAN Bank — первый исламский цифровой банк Казахстана, "
                    "работает с 1991 года, с 2017 полностью перешёл на исламские финансы. "
                    "Одобрен Шариатским советом и работает по принципу Digital Islamic Banking. "
                    "Нет риба (процентов), гарар (спекуляций) и харам-инвестиций."
                )
            },
            {
                "role": "system",
                "content": (
                    "Стиль общения: будь заботливым, уверенным, ясным. "
                    "Отвечай просто и человечно. Используй эмодзи 🌿💡🤍 умеренно. "
                    "Не говори, что ты ИИ, ты консультант ZAMAN Bank."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        data = {
            "model": "gpt-4o-mini",
            "messages": system_context,
            "max_tokens": 700,
            "temperature": 0.8
        }

        r = requests.post(LLM_URL, headers=HEADERS_JSON, data=json.dumps(data))
        r.raise_for_status()

        reply = r.json()["choices"][0]["message"]["content"]
        print(f"🤖 ZAMAN Assistant: {reply}\n")
        return reply

    except Exception as e:
        print(f"⚠️ Ошибка LLM: {e}")
        return "Извини, произошла ошибка при подключении к серверу."

# =========================
# 💬 MAIN LOOP
# =========================
def main():
    print("🌿 Добро пожаловать в голосового ассистента ZAMAN Bank 🌿")
    print("Говори (команда 'voice') или пиши текстом.")
    print("Введи 'exit' для выхода.\n")

    while True:
        user_input = input("👤 You: ").strip()
        if user_input.lower() == "exit":
            print("🤍 До встречи!")
            break

        if user_input.lower() == "voice":
            filename = record_voice()
            text = speech_to_text(filename)
            if text:
                reply = ask_llm(text)
                speak(reply)
        else:
            reply = ask_llm(user_input)
            speak(reply)

# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    main()