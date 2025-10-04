import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

# Получаем токен бота
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("❌ TELEGRAM_BOT_TOKEN не найден в файле .env!")

print(f"Токен бота загружен: {TELEGRAM_BOT_TOKEN[:10]}...")
