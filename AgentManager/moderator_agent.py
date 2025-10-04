"""
ModeratorAgent - первый агент системы Lumira
Функции: общение с пользователями, координация других агентов
"""
import config
from langchain_ollama import OllamaLLM
from langchain.schema import SystemMessage, HumanMessage
from config.Agent_config import AgentConfig
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModeratorAgent:
    """
    Агент-модератор для образовательной системы

    Основные функции:
    - Обработка сообщений пользователей
    - Генерация ответов через Ollama
    - Координация с другими агентами (в будущем)
    """

    def __init__(self):
        """Инициализация агента-модератора"""
        try:
            # Подключение к Ollama
            self.llm = OllamaLLM(
                model=AgentConfig.OLLAMA_MODEL,
                base_url=AgentConfig.OLLAMA_BASE_URL,
                temperature=AgentConfig.TEMPERATURE
            )

            # Системный промпт агента
            self.system_prompt = AgentConfig.get_system_prompt("moderator")

            # История диалога (пока простая, в памяти)
            self.conversation_history = {}

            logger.info(f"ModeratorAgent инициализирован с моделью {AgentConfig.OLLAMA_MODEL}")

        except Exception as e:
            logger.error(f"Ошибка инициализации ModeratorAgent: {e}")
            raise

    async def process_message(self, user_id: int, user_message: str) -> str:
        """
        Обработка сообщения от пользователя

        Args:
            user_id: ID пользователя в Telegram
            user_message: Текст сообщения от пользователя

        Returns:
            str: Ответ агента
        """
        try:
            # Получаем историю диалога для пользователя
            history = self.get_user_history(user_id)

            # Формируем полный промпт с контекстом
            full_prompt = self._build_prompt(user_message, history)

            # Генерируем ответ через Ollama
            response = await self._generate_response(full_prompt)

            # Сохраняем в историю
            self.update_history(user_id, user_message, response)

            logger.info(f"Обработано сообщение от пользователя {user_id}")
            return response

        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
            return "Извините, произошла ошибка. Попробуйте еще раз."

    def get_user_history(self, user_id: int) -> list:
        """Получить историю диалога пользователя"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        return self.conversation_history[user_id]

    def update_history(self, user_id: int, user_message: str, bot_response: str):
        """Обновить историю диалога"""
        history = self.get_user_history(user_id)

        # Добавляем новое сообщение
        history.append({
            "user": user_message,
            "bot": bot_response
        })

        # Ограничиваем историю последними 5 сообщениями
        if len(history) > 5:
            history.pop(0)

    def _build_prompt(self, user_message: str, history: list) -> str:
        """Построить полный промпт с учетом истории"""
        prompt_parts = [self.system_prompt]

        # Добавляем контекст из истории
        if history:
            prompt_parts.append("\nКонтекст предыдущих сообщений:")
            for msg in history[-3:]:  # Последние 3 сообщения
                prompt_parts.append(f"Пользователь: {msg['user']}")
                prompt_parts.append(f"Ты: {msg['bot']}")

        # Добавляем текущее сообщение
        prompt_parts.append(f"\nТекущее сообщение пользователя: {user_message}")
        prompt_parts.append("\nТвой ответ:")

        return "\n".join(prompt_parts)

    async def _generate_response(self, prompt: str) -> str:
        """Генерация ответа через Ollama"""
        try:
            # Вызываем Ollama для генерации ответа
            response = await self.llm.ainvoke(prompt)

            # Очищаем ответ от лишних символов
            cleaned_response = response.strip()

            return cleaned_response if cleaned_response else "Не могу ответить на этот вопрос."

        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            return "Извините, сейчас не могу ответить. Попробуйте позже."

    def reset_user_history(self, user_id: int):
        """Сброс истории диалога пользователя"""
        if user_id in self.conversation_history:
            del self.conversation_history[user_id]
            logger.info(f"История пользователя {user_id} сброшена")
