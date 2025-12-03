"""
Пакет AgentManager - управление агентами
"""
from AgentManager.gigachat_auth import GigaChatAuth, get_gigachat_client
from AgentManager.base_agent import BaseAgent
from AgentManager.moderator_agent import ModeratorAgent
from AgentManager.tutor_agent import TutorAgent
from AgentManager.examiner_agent import ExaminerAgent

__all__ = [
    "GigaChatAuth",
    "get_gigachat_client",
    "BaseAgent",
    "ModeratorAgent",
    "TutorAgent",
    "ExaminerAgent"
]
