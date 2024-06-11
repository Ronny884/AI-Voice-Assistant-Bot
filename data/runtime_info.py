import asyncio
from openai_operations import ai_actions as api


class UsersRuntimeInfo:
    def __init__(self):
        self.data = {}
        self.assistant = None

    instance = None

    # реализация паттерна Singleton необходима для комфортной работы
    # с экземпляром класса из разных модулей
    def __new__(cls):
        if UsersRuntimeInfo.instance is None:
            UsersRuntimeInfo.instance = super().__new__(cls)
        return UsersRuntimeInfo.instance

    async def create_assistant(self):
        self.assistant = await api.create_assistant()

    async def load_assistant(self):
        self.assistant = await api.load_assistant()





