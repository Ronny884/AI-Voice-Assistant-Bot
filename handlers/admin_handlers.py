from aiogram import Router, types
from aiogram.types import Message
from aiogram.filters.command import Command
from config.config_reader import config
from filters.is_admin import IsAdminFilter
from data.runtime_info import UsersRuntimeInfo

router = Router()
info = UsersRuntimeInfo()


@router.message(Command("start"), IsAdminFilter(config.admin))
async def cmd_start(message: types.Message):
    await message.answer("Чат администратора")

    # сброс контекста
    if message.chat.id in info.data:
        del info.data[message.chat.id]
