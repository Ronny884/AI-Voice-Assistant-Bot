from aiogram import Router, types
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from config.config_reader import config
from filters.is_admin import IsAdminFilter
from data.runtime_info import UsersRuntimeInfo
from analytics.amplitude_work import *
from handlers.own_handlers import del_context
from db import orm, statistics

router = Router()
# info = UsersRuntimeInfo()


@router.message(Command("start"), IsAdminFilter(config.admin))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer("Чат администратора")

    # перезапуск бота предполагает сброс контекста
    await del_context(message, state, True)

    # запись в БД
    if await orm.user_exists(message.from_user.id) is False:
        await orm.insert_user(message.from_user.id)

        # ивент по добавлению в БД
        amplitude_executor.submit(track_event, 6, config.admin)

    # ивент по нажатию start
    amplitude_executor.submit(track_event, 1, config.admin)


@router.message(Command("statistic"), IsAdminFilter(config.admin))
async def get_statistic(message: types.Message):

    # мини-статистика администратора
    count_of_users = await statistics.AdminStatistics.get_count_of_users()
    the_most_active_user = await statistics.AdminStatistics.get_the_most_active_user()
    the_most_popular_value = await statistics.AdminStatistics.get_the_most_popular_value()
    statistic = \
        f"""
Количество пользователей в БД: {str(count_of_users)}\n
Самый активный пользователь: {str(the_most_active_user)}\n
Наиболее частая ценность среди пользователей: {str(the_most_popular_value)}
"""
    await message.answer(statistic)
