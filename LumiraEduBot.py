"""
Lumira Educational Bot - основной файл телеграм-бота
Интеграция с LLM-агентами для образовательных целей
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F
from dotenv import load_dotenv
import os


# Импортируем нашего агента-модератора
from AgentManager.moderator_agent import ModeratorAgent

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LumiraBot:
    """Главный класс телеграм-бота Lumira"""

    def __init__(self):
        """Инициализация бота и агентов"""
        # Получаем токен бота
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env файле")

        # Инициализируем бот и диспетчер
        self.bot = Bot(token=token)
        self.dp = Dispatcher()

        # Инициализируем агента-модератора
        self.moderator_agent = ModeratorAgent()

        # Регистрируем обработчики
        self._register_handlers()

        logger.info("LumiraBot инициализирован успешно")

    def _register_handlers(self):
        """Регистрация обработчиков сообщений"""

        # Обработчик команды /start
        @self.dp.message(Command("start"))
        async def cmd_start(message: Message):
            """Обработка команды /start"""
            await self.handle_start_command(message)

        # Обработчик команды /help
        @self.dp.message(Command("help"))
        async def cmd_help(message: Message):
            """Обработка команды /help"""
            await self.handle_help_command(message)

        # Обработчик команды /reset
        @self.dp.message(Command("reset"))
        async def cmd_reset(message: Message):
            """Обработка команды /reset"""
            await self.handle_reset_command(message)

        # Обработчик всех текстовых сообщений
        @self.dp.message(F.text)
        async def handle_text_message(message: Message):
            """Обработка текстовых сообщений через агента"""
            await self.handle_user_message(message)

    async def handle_start_command(self, message: Message):
        """Обработка команды /start"""
        welcome_text = """
🎓 Добро пожаловать в Lumira Educational Bot!

Я - ваш персональный помощник в обучении.
Сейчас работает агент-модератор, который поможет вам с учебными вопросами.

Команды:
/help - помощь
/reset - сброс истории диалога

Просто напишите мне любой вопрос!
        """
        await message.answer(welcome_text)
        logger.info(f"Пользователь {message.from_user.id} запустил бота")

    async def handle_help_command(self, message: Message):
        """Обработка команды /help"""
        help_text = """
📚 Lumira Educational Bot - Помощь

🤖 Доступные агенты:
• ModeratorAgent - основной помощник (активен)

💬 Как пользоваться:
• Пишите любые вопросы
• Бот запоминает контекст разговора
• Используйте /reset для очистки истории

🔧 Команды:
• /start - начать работу
• /help - эта справка
• /reset - сброс диалога
        """
        await message.answer(help_text)

    async def handle_reset_command(self, message: Message):
        """Обработка команды /reset"""
        user_id = message.from_user.id

        # Сбрасываем историю в агенте
        self.moderator_agent.reset_user_history(user_id)

        await message.answer("✅ История диалога сброшена. Можем начать заново!")
        logger.info(f"Сброшена история для пользователя {user_id}")

    async def handle_user_message(self, message: Message):
        """Обработка обычных сообщений пользователя"""
        try:
            user_id = message.from_user.id
            user_message = message.text

            # Отправляем сообщение агенту-модератору
            agent_response = await self.moderator_agent.process_message(
                user_id=user_id,
                user_message=user_message
            )

            # Отправляем ответ пользователю
            await message.answer(agent_response)

            logger.info(f"Обработано сообщение от {user_id}: {user_message[:50]}...")

        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            await message.answer(
                "😔 Извините, произошла ошибка. Попробуйте еще раз или используйте /reset"
            )

    async def start_polling(self):
        """Запуск бота в режиме polling"""
        try:
            logger.info("Запуск Lumira Bot...")
            await self.dp.start_polling(self.bot)
        except Exception as e:
            logger.error(f"Ошибка запуска бота: {e}")
        finally:
            await self.bot.session.close()


# Функция для запуска бота
async def main():
    """Главная функция запуска"""
    try:
        # Создаем и запускаем бота
        lumira_bot = LumiraBot()
        await lumira_bot.start_polling()
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")


if __name__ == "__main__":
    # Запускаем бота
    asyncio.run(main())
