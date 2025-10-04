"""
Конфигурация для LLM-агентов
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()


class AgentConfig:
    """Базовая конфигурация для всех агентов"""

    # Ollama настройки
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    # Общие настройки агентов
    MAX_TOKENS = 500
    TEMPERATURE = 0.7

    # Системные промпты для разных агентов
    SYSTEM_PROMPTS = {
        "moderator": """
Ты - ModeratorAgent, дружелюбный модератор образовательного бота Lumira.
Твоя роль:
- Общаться с пользователями вежливо и профессионально
- Помогать с учебными вопросами
- Координировать работу других агентов (в будущем)
- Поддерживать мотивацию студентов

Отвечай кратко, по существу, и всегда дружелюбно.
Если не знаешь ответ - честно признавай это.
"""
    }

    @classmethod
    def get_system_prompt(cls, agent_type: str) -> str:
        """Получить системный промпт для конкретного типа агента"""
        return cls.SYSTEM_PROMPTS.get(agent_type, "Ты полезный помощник.")
