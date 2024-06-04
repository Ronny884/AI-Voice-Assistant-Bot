class UsersRuntimeInfo:
    def __init__(self):
        self.data = {}

    instance = None

    # реализация паттерна Singleton необходима для корректной работы
    # с экземпляром класса из разных модулей
    def __new__(cls):
        if UsersRuntimeInfo.instance is None:
            UsersRuntimeInfo.instance = super().__new__(cls)
        return UsersRuntimeInfo.instance

