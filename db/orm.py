import asyncio
from sqlalchemy import text, select
from db.database import *
from db.models import *


# проверка есть ли данный пользователь в таблице
async def user_exists(user_id):
    async with async_session_factory() as session:
        user = await session.get(UsersORM, user_id)
    return user is not None


# добавление нового пользователя с дефолтными настройками
async def insert_user(user_telegram_id):
    async with async_session_factory() as session:
        user = UsersORM(telegram_id=user_telegram_id,
                        message_count=0,
                        voice='alloy')
        session.add(user)
        await session.commit()


# увеличения счётчика голосовых сообщений пользователя на 1
async def update_user_voice_message_count(user_id):
    async with async_session_factory() as session:
        user = await session.get(UsersORM, user_id)
        user.message_count += 1
        await session.commit()


# проверка есть ли ценность с конкретным названием у конкретного пользователя
async def value_exists(user_id, value_name):
    async with async_session_factory() as session:
        query = select(ValuesORM).filter_by(telegram_id=user_id, name=value_name)
        result = await session.execute(query)
        value = result.all()
        if value:
            return True
        else:
            return False


# увеличение рейтинга конкретной ценности у конкретного пользователя на 1
async def update_value_rating(user_id, value_name):
    async with async_session_factory() as session:
        query = select(ValuesORM).filter_by(telegram_id=user_id, name=value_name)
        result = await session.execute(query)
        value = result.scalars().all()[0]
        value.rating += 1
        await session.commit()


# добавление новой ценности, уникальной для данного пользователя
async def insert_value(user_id, value_name):
    async with async_session_factory() as session:
        value = ValuesORM(
                          name=value_name,
                          rating=1,
                          telegram_id=user_id)
        session.add(value)
        await session.commit()


