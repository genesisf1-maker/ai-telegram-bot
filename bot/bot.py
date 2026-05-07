import os
import telebot

TOKEN = os.getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🚀 Bot Railway orqali ishlamoqda!")

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.reply_to(message, f"Siz yozdingiz: {message.text}")

print("🚀 Railway bot ishga tushdi...")

bot.infinity_polling()
