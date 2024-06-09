import asyncio
from openai_operations import ai_actions as api


class UsersRuntimeInfo:
    def __init__(self):
        self.data = {}
        self.based_assistant = None
        self.values_assistant = None

    instance = None

    # реализация паттерна Singleton необходима для корректной работы
    # с экземпляром класса из разных модулей
    def __new__(cls):
        if UsersRuntimeInfo.instance is None:
            UsersRuntimeInfo.instance = super().__new__(cls)
        return UsersRuntimeInfo.instance

    async def create_assistants(self):
        self.based_assistant = await api.create_based_assistant()
        self.values_assistant = await api.create_values_assistant()

    async def load_assistants(self):
        self.based_assistant = await api.load_based_assistant()
        self.values_assistant = await api.load_values_assistant()




