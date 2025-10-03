import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from config.Bot_config import BOT_TOKEN

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_command(message: Message):
    """Обработчик команды /start"""
    user_name = message.from_user.first_name

    welcome_text = f"""
👋 Привет, {user_name}!

🤖 Я простой телеграм-бот для тестирования.

📋 Мои команды:
/start - Начать работу с ботом
/help - Показать справку

💬 Просто напишите мне что-нибудь!
"""

    await message.answer(welcome_text)


@dp.message(Command("help"))
async def help_command(message: Message):
    """Справка по боту"""
    help_text = """
🆘 <b>Справка по боту</b>

📋 <b>Команды:</b>
• /start - Начать работу
• /help - Эта справка
"""

    await message.answer(help_text, parse_mode="HTML")

# Обработчики текстовых сообщений
@dp.message(F.text.lower().contains("привет") | F.text.lower().contains("hello"))
async def hello_handler(message: Message):
    """Приветствие"""
    user_name = message.from_user.first_name
    greetings = [
        f"👋 Привет, {user_name}!",
        f"🤗 Здравствуй, {user_name}!",
        f"😊 Приветствую, {user_name}!",
        f"🎉 О, привет, {user_name}!"
    ]

    import random
    greeting = random.choice(greetings)
    await message.answer(greeting)


async def main():
    """Запуск бота"""
    print("🤖 Запуск простого бота...")
    print("⏹️ Для остановки нажмите Ctrl+C")

    try:
        # Запускаем бота
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        print("\n⏹️ Бот остановлен")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
