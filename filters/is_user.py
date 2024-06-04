from aiogram.types import Message
from aiogram.filters import BaseFilter


class IsUserFilter(BaseFilter):
    def __init__(self, admin_id):
        self.admin_id = admin_id

    async def __call__(self, message: Message):
        return message.from_user.id != self.admin_id
