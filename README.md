# ai-telegram-bot
AI-powered Telegram bot with smart memory, deep thinking, and personal development focus. Supports text and image analysis, autonomous messaging, and strategic responses. Built for scalability and real-world usage.
import os
import telebot
import requests
import json
import time
import random
from datetime import datetime
import threading
from dotenv import load_dotenv
from flask import Flask

# ================== LOAD ENV ==================
load_dotenv()

BOT_TOKEN = os.getenv("8449766015:AAHHr-u6GN4xa-4cxBeE_ejiWFVCTTlESK4")
API_KEY = os.getenv("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")
MODEL = os.getenv("MODEL", "openai/gpt-4o")

if not BOT_TOKEN or not API_KEY:
    print("❌ ENV topilmadi! .env faylni tekshir yoki Render muhit o'zgaruvchilarini sozla")
    exit()

bot = telebot.TeleBot(BOT_TOKEN)

# ================== DUMMY WEB SERVER (RENDER UCHUN) ==================
# Render loyihani yopib qo'ymasligi uchun soxta veb-server yaratamiz
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot faol va ishlamoqda!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ================== MEMORY ==================
user_memory = {}

def get_memory(uid):
    return user_memory.get(uid, "")

def update_memory(uid, text):
    if uid not in user_memory:
        user_memory[uid] = ""
    user_memory[uid] += f"\n{text}"
    user_memory[uid] = user_memory[uid][-2000:]

# ================== AI RESPONSE ==================
def get_ai_response(uid, user_text):
    try:
        memory = get_memory(uid)
        system_prompt = """
Sen aqlli, strategik va kuchli AI yordamchisan.
Qoidalar:
- Asosan o‘zbek tilida yoz
- Qisqa, aniq va tushunarli bo‘l
- Keraksiz rasmiy gap ishlatma
- Foydali maslahat ber
- Har javobda qiymat (value) bo‘lsin
DeepThink:
- Savolni chuqur tushun
- Sabab → yechim → natija formatida yoz
- Agar kerak bo‘lsa reja tuz
"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Kontekst:\n{memory}\n\nSavol:\n{user_text}"}
        ]

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": messages,
                "max_tokens": 800,
                "temperature": 0.7
            },
            timeout=20
        )

        data = response.json()
        if "choices" not in data:
            print("API ERROR:", data)
            return "⚠️ AI API bilan bog'lanishda muammo yuz berdi."

        reply = data["choices"][0]["message"]["content"]
        update_memory(uid, f"User: {user_text}\nAI: {reply}")
        return reply

    except Exception as e:
        print("AI ERROR:", e)
        return "❌ Xatolik yuz berdi"

# ================== OCR (TESSERACT O'RNIGA CLOUD API) ==================
def read_image(file_path):
    try:
        url = 'https://api.ocr.space/parse/image'
        with open(file_path, 'rb') as f:
            payload = {'apikey': 'helloworld', 'language': 'eng'}
            res = requests.post(url, files={'file': f}, data=payload, timeout=20)
        
        if res.status_code == 200:
            result = res.json()
            if not result.get('IsErroredOnProcessing'):
                return result['ParsedResults'][0]['ParsedText'][:2000]
        return ""
    except Exception as e:
        print("OCR ERROR:", e)
        return ""

# ================== HANDLERS ==================
@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🚀 Salom! Men aqlli AI yordamchiman. Savol ber yoki rasm yubor.")

@bot.message_handler(content_types=['text'])
def handle_text(msg):
    uid = msg.chat.id
    bot.send_chat_action(uid, 'typing')
    reply = get_ai_response(uid, msg.text)
    bot.reply_to(msg, reply)

@bot.message_handler(content_types=['photo'])
def handle_photo(msg):
    try:
        uid = msg.chat.id
        bot.send_chat_action(uid, 'typing')
        
        file_info = bot.get_file(msg.photo[-1].file_id)
        downloaded = bot.download_file(file_info.file_path)
        file_path = f"file_{uid}.jpg"

        with open(file_path, "wb") as f:
            f.write(downloaded)

        text = read_image(file_path)
        
        if os.path.exists(file_path):
            os.remove(file_path)

        if not text or len(text.strip()) < 5:
            bot.reply_to(msg, "⚠️ Rasmda matn topilmadi yoki o'qib bo'lmadi.")
            return

        prompt = f"Rasm ichidagi matn:\n\n{text}\n\nVazifa:\n1. Qisqa xulosa\n2. Muhim nuqtalar\n3. Amaliy foyda"
        reply = get_ai_response(uid, prompt)
        bot.reply_to(msg, reply)

    except Exception as e:
        print("IMAGE ERROR:", e)
        bot.reply_to(msg, "❌ Rasmni o‘qib bo‘lmadi")

# ================== AUTO MESSAGE ==================
def auto_message():
    while True:
        try:
            hour = datetime.now().hour
            if 9 <= hour <= 22:
                for uid in user_memory.keys():
                    msg = random.choice([
                        "🔥 Bugun 1% yaxshiroq bo‘lish uchun nima qilding?",
                        "🚀 Maqsadingni esla. Bugun nima qadam tashlaysan?",
                        "💡 Intizom = muvaffaqiyat. Davom et!"
                    ])
                    bot.send_message(uid, msg)
            time.sleep(random.randint(7200, 10800))  # 2-3 soat
        except Exception as e:
            print("AUTO ERROR:", e)

# ================== RUN ALL ==================
if __name__ == "__main__":
    # 1. Flask veb-serverni alohida thread'da ishga tushiramiz
    threading.Thread(target=run_web, daemon=True).start()
    
    # 2. Avtomatik xabarlar tizimi
    threading.Thread(target=auto_message, daemon=True).start()

    # 3. Asosiy bot
    print("🚀 Bot va Web Server ishga tushdi...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
