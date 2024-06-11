from aiogram import Router, types
from aiogram.types import Message
from aiogram.filters.command import Command
from config.config_reader import config
from filters.is_user import IsUserFilter
from data.runtime_info import UsersRuntimeInfo
from analytics.amplitude_work import *
from db import orm

router = Router()
info = UsersRuntimeInfo()


@router.message(Command("start"), IsUserFilter(config.admin))
async def cmd_start(message: types.Message):
    await message.answer("Здравствуйте! Вас приветствует голосовой AI-ассистент.\n"
                         "Версия GPT-4o.\n"
                         "Запишите ваше голосовое сообщение!)\n"
                         "\n"
                         "Команды:\n"
                         "/start - перезапуск бота\n"
                         "/del - сброс контекста")

    # сброс контекста
    if message.chat.id in info.data:
        del info.data[message.chat.id]

    # проверка, есть ли пользователь в БД
    if await orm.user_exists(message.from_user.id) is False:
        await orm.insert_user(message.from_user.id)

        # ивент по добавлению в БД
        amplitude_executor.submit(add_to_db_event, message.from_user.id)

        # при подключении нового пользователя идёт оповещение в чат администратора
        await message.bot.send_message(chat_id=config.admin,
                                       text=f'Новый пользователь:\n'
                                            f'id: {message.chat.id}\n'
                                            f'ник: {message.chat.username}')

    # ивент по нажатию start
    amplitude_executor.submit(command_start_event, message.from_user.id)

