import asyncio
from openai_operations import ai_actions as api
from openai_operations.file_work import FileWorker


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
        print('asst', self.assistant.id)

    async def load_assistant(self):
        self.assistant = await api.load_assistant()

    # создание нового векторного хранилища и загрузка туда документа
    # апдейт существующего ассистента
    async def create_vector_store_and_update_assistant(self):
        vector_store = await FileWorker.create_vector_store()
        await FileWorker.add_file_to_vector_store(vector_store.id)
        await FileWorker.update_assistant(self.assistant.id, vector_store.id)








