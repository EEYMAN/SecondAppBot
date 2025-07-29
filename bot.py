import os
import asyncio
from flask import Flask, send_from_directory
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from waitress import serve

API_TOKEN = '8178668402:AAHhnaR4idzlp1Nglg9FmsrIM8uci4OydW4'
WEBAPP_URL = "https://appbot-production-c01e.up.railway.app"  # Railway-домен

# === Flask-приложение ===
flask_app = Flask(__name__, static_folder="web")

@flask_app.route("/")
def index():
    return send_from_directory("web", "index.html")

# === Telegram-бот ===
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# === Локализация ===
locales = {
    'ru': {
        'welcome': "👋 Добро пожаловать! Нажмите кнопку ниже, чтобы открыть Аналитик Sigma.",
        'terminal_hint': "Кнопка терминала доступна ниже 👇",
        'terminal_button': "🔥 Открыть бота Sigma 🔥"
    },
    'uk': {
        'welcome': "👋 Ласкаво просимо! Натисніть кнопку нижче, щоб відкрити Аналітик Sigma.",
        'terminal_hint': "Кнопка терміналу доступна нижче 👇",
        'terminal_button': "🔥 Відкрити бота Sigma 🔥"
    },
    'en': {
        'welcome': "👋 Welcome! Click the button below to open the Analyst Sigma.",
        'terminal_hint': "Terminal button is available below 👇",
        'terminal_button': "🔥 Open bot Sigma 🔥"
    }
}

# Получение локализации на основе языка пользователя
def get_locale(message: types.Message) -> dict:
    lang_code = (message.from_user.language_code or 'ru')[:2]
    return locales.get(lang_code, locales['en'])

# Клавиатура с учётом локализации
def get_persistent_keyboard(loc: dict):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    keyboard.add(KeyboardButton(
        text=loc['terminal_button'],
        web_app=WebAppInfo(url=WEBAPP_URL)
    ))
    return keyboard

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    loc = get_locale(message)
    keyboard = get_persistent_keyboard(loc)
    await message.answer(loc['welcome'], reply_markup=keyboard)

@dp.message_handler()
async def always_show_keyboard(message: types.Message):
    loc = get_locale(message)
    keyboard = get_persistent_keyboard(loc)
    await message.answer(loc['terminal_hint'], reply_markup=keyboard)

# === Асинхронный запуск Flask и Telegram ===
async def main():
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, lambda: serve(flask_app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080))))
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())

