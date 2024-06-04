import os
import asyncio
import logging
from aiogram import Bot, Dispatcher
from config.config_reader import config
from handlers import user_handlers, admin_handlers, own_handlers


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(config.token.get_secret_value())
    dp = Dispatcher()
    dp.include_routers(user_handlers.router, admin_handlers.router, own_handlers.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
