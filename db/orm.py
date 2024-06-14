import asyncio
import logging
from sqlalchemy import text, select
from db.database import *
from db.models import *


# проверка есть ли данный пользователь в таблице
async def user_exists(user_id):
    try:
        async with async_session_factory() as session:
            user = await session.get(UsersORM, user_id)
        return user is not None
    except Exception as e:
        logging.error(e)


# добавление нового пользователя с дефолтными настройками
async def insert_user(user_telegram_id):
    try:
        async with async_session_factory() as session:
            user = UsersORM(telegram_id=user_telegram_id,
                            message_count=0,
                            voice='alloy')
            session.add(user)
            await session.commit()
    except Exception as e:
        logging.error(e)


# увеличения счётчика сообщений пользователя на 1
async def update_user_message_count(user_id):
    try:
        async with async_session_factory() as session:
            user = await session.get(UsersORM, user_id)
            user.message_count += 1
            await session.commit()
    except Exception as e:
        logging.error(e)


# проверка есть ли ценность с конкретным названием у конкретного пользователя
async def value_exists(user_id, value_name):
    try:
        async with async_session_factory() as session:
            query = select(ValuesORM).filter_by(telegram_id=user_id, name=value_name)
            result = await session.execute(query)
            value = result.all()
            if value:
                return True
            else:
                return False
    except Exception as e:
        logging.error(e)


# увеличение рейтинга конкретной ценности у конкретного пользователя на 1
async def update_value_rating(user_id, value_name):
    try:
        async with async_session_factory() as session:
            query = select(ValuesORM).filter_by(telegram_id=user_id, name=value_name)
            result = await session.execute(query)
            value = result.scalars().all()[0]
            value.rating += 1
            await session.commit()
    except Exception as e:
        logging.error(e)


# добавление новой ценности, уникальной для данного пользователя
async def insert_value(user_id, value_name):
    try:
        async with async_session_factory() as session:
            value = ValuesORM(
                name=value_name,
                rating=1,
                telegram_id=user_id)
            session.add(value)
            await session.commit()
    except Exception as e:
        logging.error(e)


# голос бота, настроенный у пользователя
async def get_voice(user_id):
    try:
        async with async_session_factory() as session:
            user = await session.get(UsersORM, user_id)
        return user.voice
    except Exception as e:
        logging.error(e)


# установка голоса бота
async def set_voice(user_id, new_voice):
    try:
        async with async_session_factory() as session:
            user = await session.get(UsersORM, user_id)
            user.voice = new_voice
            await session.commit()
    except Exception as e:
        logging.error(e)
