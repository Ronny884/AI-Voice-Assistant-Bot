import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from config.config_reader import config
from data.runtime_info import UsersRuntimeInfo
from handlers import user_handlers, admin_handlers, own_handlers
from db.database import DatabaseCreator


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(config.token.get_secret_value())
    dp = Dispatcher()
    dp.include_routers(user_handlers.router, admin_handlers.router, own_handlers.router)
    info = UsersRuntimeInfo()

    # создание таблиц, если их не существует
    await DatabaseCreator.create_table_users()
    await DatabaseCreator.create_table_values()

    await info.create_assistant()
    # await info.load_assistant()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
