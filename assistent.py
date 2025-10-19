import os
import json
import sounddevice as sd
import soundfile as sf
import requests
from gtts import gTTS
import playsound
import warnings
import urllib3

# =========================
# ⚙️ CONFIGURATION
# =========================
warnings.filterwarnings("ignore", category=UserWarning)
urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)

OPENAI_KEY = "key"  # твой ключ сюда
LLM_URL = "https://api.openai.com/v1/chat/completions"
WHISPER_URL = "https://api.openai.com/v1/audio/transcriptions"

HEADERS_JSON = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_KEY}"
}
HEADERS_WHISPER = {"Authorization": f"Bearer {OPENAI_KEY}"}

# =========================
# 🎙 RECORD VOICE
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
# 🔊 SPEECH → TEXT
# =========================
def speech_to_text(filename):
    print("🔊 Распознаю речь...")
    try:
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "audio/wav")}
            data = {"model": "whisper-1", "language": "ru"}
            r = requests.post(WHISPER_URL, headers=HEADERS_WHISPER, files=files, data=data)
            r.raise_for_status()
            return r.json().get("text", "").strip()
    except Exception as e:
        print(f"⚠️ Ошибка Whisper: {e}")
        return ""

# =========================
# 🔈 TEXT → VOICE
# =========================
def speak(text, filename="reply.mp3"):
    print("🔊 Озвучиваю ответ...")
    try:
        tts = gTTS(text=text, lang="ru")
        tts.save(filename)
        playsound.playsound(filename)
        os.remove(filename)
    except Exception as e:
        print(f"⚠️ Ошибка TTS: {e}")

# =========================
# 🧠 ASK GPT
# =========================
def ask_llm(prompt):
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "Ты — ассистент ZAMAN Bank 🌿 "
                    "Говори спокойно, дружелюбно и с уважением. "
                    "Не называй себя ИИ, ты консультант банка."
                )
            },
            {"role": "user", "content": prompt}
        ]
        data = {
            "model": "gpt-4o-mini",
            "messages": messages,
            "max_tokens": 700,
            "temperature": 0.8
        }
        r = requests.post(LLM_URL, headers=HEADERS_JSON, data=json.dumps(data))
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"⚠️ Ошибка LLM: {e}")
        return "Извини, возникла ошибка при подключении к серверу."
